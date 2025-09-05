from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastmcp import Client
from google import genai
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing clients...")
    
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    service_account_email = "YOUR_SERVICE_ACCOUNT_EMAIL@YOUR_PROJECT_ID.iam.gserviceaccount.com"

    try:
        auth_headers = {}
        if "K_SERVICE" in os.environ:
            # Cloud Run environment
            auth_request = Request()
            id_token = google.oauth2.id_token.fetch_id_token(
                auth_request, audience=mcp_server_url
            )
            auth_headers = {"Authorization": f"Bearer {id_token}"}
            print(f"Fetched ID token for audience {mcp_server_url}")
        else:
            # Local development environment with impersonation
            print("Local environment detected. Impersonating service account.")
            
            # Use gcloud ADC to get user credentials
            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            
            # Impersonate the service account to get an ID token
            impersonated_credentials = ServiceAccountCredentials.from_impersonated_credentials(
                source_credentials=credentials,
                target_principal=service_account_email,
                target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
                lifetime=300 # seconds
            )
            
            # The impersonated credentials will have a valid token
            if impersonated_credentials.token:
                id_token = impersonated_credentials.token
                auth_headers = {"Authorization": f"Bearer {id_token}"}
                print("Successfully generated ID token via impersonation.")
            else:
                raise ValueError("Failed to generate impersonated token.")

        # Continue with client initialization
        async with Client(mcp_server_url, headers=auth_headers) as mcp_client:
            app.state.mcp_client = mcp_client
            print("FastMCP client session is ready.")
            tools = await mcp_client.list_tools()
            print("Available tools:", [tool.name for tool in tools])

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set.")
            app.state.gemini_client = genai.Client(api_key=api_key)
            print("Gemini client is ready.")
            
            yield
            
            print("Clients session closed.")

    except Exception as e:
        print(f"Error during client lifespan management: Client failed to connect: {e}")
        yield