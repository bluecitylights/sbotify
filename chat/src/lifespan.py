from contextlib import asynccontextmanager
import os
import logging
from fastapi import FastAPI
from fastmcp import Client
from google import genai
from google.oauth2 import id_token
from google.auth.transport.requests import Request

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing clients...")
    
    # Store clients that will be kept alive
    app.state.mcp_client = None
    app.state.gemini_client = None
    
    # Use different connection strategies for different environments
    if "K_SERVICE" in os.environ:
        # Cloud Run production - use actual service URL with auth
        mcp_server_url = os.getenv("MCP_SERVER_URL")
        logger.info("Cloud Run environment - using service-to-service authentication")
        
        try:
            # Get ID token for service-to-service auth
            auth_request = Request()
            token = id_token.fetch_id_token(auth_request, mcp_server_url)
            logger.info("Successfully obtained Cloud Run identity token")
            print(token)
            # Create and store the client (keep connection alive)
            app.state.mcp_client = Client(f"{mcp_server_url}/mcp", auth=token)
            await app.state.mcp_client.__aenter__()  # Start the connection
            logger.info("MCP client connected successfully (Cloud Run)")
                
        except Exception as e:
            logger.error(f"Cloud Run MCP connection failed: {e}")
            app.state.mcp_client = None
    
    else:
        # Local development - use environment variable or default to proxy tunnel
        mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")
        logger.info(f"Local development - connecting to: {mcp_server_url}")
        if mcp_server_url.startswith("http://localhost"):
            logger.info("Using local URL - make sure gcloud proxy is running if needed:")
            logger.info("gcloud run services proxy sbotify-mcp-server --region=europe-west4")
        
        try:
            # Create and store the client (keep connection alive)
            app.state.mcp_client = Client(mcp_server_url)
            await app.state.mcp_client.__aenter__()  # Start the connection
            logger.info(f"MCP client connected successfully to: {mcp_server_url}")
            
            # List available tools for debugging
            try:
                tools = await app.state.mcp_client.list_tools()
                tool_names = [tool.name for tool in tools]
                logger.info(f"Available MCP tools: {tool_names}")
            except Exception as e:
                logger.warning(f"Could not list MCP tools: {e}")
                
        except Exception as e:
            logger.error(f"MCP connection failed to {mcp_server_url}: {e}")
            if mcp_server_url.startswith("http://localhost"):
                logger.info("If using gcloud proxy, make sure it's running:")
                logger.info("gcloud run services proxy sbotify-mcp-server --region=europe-west4")
            app.state.mcp_client = None
    
    # Initialize Gemini client (same for both environments)
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        app.state.gemini_client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialized successfully")
        
    except Exception as e:
        logger.error(f"Gemini client initialization failed: {e}")
        app.state.gemini_client = None
    
    # Report initialization status
    mcp_status = "✅ Connected" if app.state.mcp_client else "❌ Failed"
    gemini_status = "✅ Connected" if app.state.gemini_client else "❌ Failed"
    logger.info(f"Initialization complete - MCP: {mcp_status}, Gemini: {gemini_status}")
    
    yield
    
    logger.info("Shutting down clients...")
    
    # Properly close the MCP client connection
    if app.state.mcp_client:
        try:
            await app.state.mcp_client.__aexit__(None, None, None)
            logger.info("MCP client connection closed")
        except Exception as e:
            logger.warning(f"Error closing MCP client: {e}")
    
    # Gemini client doesn't need explicit cleanup

# Optional: Health check function
def get_client_status(app: FastAPI) -> dict:
    """Get the current status of all clients."""
    return {
        "mcp_client": bool(getattr(app.state, 'mcp_client', None)),
        "gemini_client": bool(getattr(app.state, 'gemini_client', None)),
        "environment": "cloud_run" if "K_SERVICE" in os.environ else "local_development"
    }