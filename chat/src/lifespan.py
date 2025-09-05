from contextlib import asynccontextmanager
import os
import logging
from fastapi import FastAPI
from fastmcp import Client
from google import genai
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google.auth import impersonated_credentials

# Set up structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing clients...")
    
    # Configuration
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    service_account_email = os.getenv("SERVICE_ACCOUNT_EMAIL")
    
    if not service_account_email:
        logger.error("SERVICE_ACCOUNT_EMAIL environment variable not set")
        raise ValueError("SERVICE_ACCOUNT_EMAIL environment variable is required")
    
    try:
        auth_headers = await _get_auth_headers(mcp_server_url, service_account_email)
        
        # Initialize MCP client
        async with Client(mcp_server_url, headers=auth_headers) as mcp_client:
            app.state.mcp_client = mcp_client
            logger.info("FastMCP client session established successfully")
            
            # Log available tools for debugging
            try:
                tools = await mcp_client.list_tools()
                tool_names = [tool.name for tool in tools]
                logger.info(f"Available MCP tools: {tool_names}")
            except Exception as e:
                logger.warning(f"Could not list MCP tools: {e}")
            
            # Initialize Gemini client
            app.state.gemini_client = _initialize_gemini_client()
            logger.info("Gemini client initialized successfully")
            
            logger.info("All clients initialized successfully")
            yield
            
            logger.info("Shutting down clients...")

    except Exception as e:
        logger.error(f"Failed to initialize clients: {str(e)}", exc_info=True)
        # Still yield to allow FastAPI to start, but without clients
        # You might want to implement health checks to verify client availability
        yield

async def _get_auth_headers(audience: str, service_account_email: str) -> dict:
    """Get authentication headers for the given audience."""
    
    if "K_SERVICE" in os.environ:
        # Cloud Run environment - use metadata service
        logger.info("Cloud Run environment detected")
        return await _get_cloud_run_auth_headers(audience)
    else:
        # Local development - use impersonation
        logger.info("Local development environment detected")
        return await _get_local_auth_headers(audience, service_account_email)

async def _get_cloud_run_auth_headers(audience: str) -> dict:
    """Get ID token in Cloud Run environment using metadata service."""
    try:
        auth_request = Request()
        token = id_token.fetch_id_token(auth_request, audience)
        logger.info(f"Successfully fetched ID token for audience: {audience}")
        return {"Authorization": f"Bearer {token}"}
    except Exception as e:
        logger.error(f"Failed to fetch ID token in Cloud Run: {e}")
        raise

async def _get_local_auth_headers(audience: str, service_account_email: str) -> dict:
    """Get ID token via service account impersonation for local development."""
    try:
        # Get ADC credentials
        source_credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        logger.info(f"Using project: {project_id}")
        
        # Create impersonated credentials specifically for ID tokens
        # Note: IDTokenCredentials constructor parameters are different
        target_credentials = impersonated_credentials.IDTokenCredentials(
            source_credentials,  # First positional parameter
            target_principal=service_account_email,
            target_audience=audience,
            include_email=True
        )
        
        # Refresh to get the token
        auth_request = Request()
        target_credentials.refresh(auth_request)
        
        if not target_credentials.token:
            raise ValueError("Failed to obtain ID token via impersonation")
        
        logger.info(f"Successfully impersonated {service_account_email} for audience: {audience}")
        return {"Authorization": f"Bearer {target_credentials.token}"}
        
    except Exception as e:
        logger.error(f"Failed to impersonate service account: {e}")
        raise

def _initialize_gemini_client():
    """Initialize Gemini client with proper error handling."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    try:
        client = genai.Client(api_key=api_key)
        logger.info("Gemini client created successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create Gemini client: {e}")
        raise

# Optional: Add a health check function
async def health_check(app: FastAPI) -> dict:
    """Check if all clients are healthy."""
    status = {
        "mcp_client": False,
        "gemini_client": False,
        "overall": False
    }
    
    # Check MCP client
    try:
        if hasattr(app.state, 'mcp_client') and app.state.mcp_client:
            # You could add a simple ping/health check to your MCP server
            status["mcp_client"] = True
    except Exception as e:
        logger.warning(f"MCP client health check failed: {e}")
    
    # Check Gemini client
    try:
        if hasattr(app.state, 'gemini_client') and app.state.gemini_client:
            status["gemini_client"] = True
    except Exception as e:
        logger.warning(f"Gemini client health check failed: {e}")
    
    status["overall"] = status["mcp_client"] and status["gemini_client"]
    return status