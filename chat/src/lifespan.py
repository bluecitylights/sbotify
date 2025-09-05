from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastmcp import Client
from google import genai

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the FastMCP and Gemini clients.
    """
    print("Initializing clients...")
    
    try:
        # Initialize the FastMCP client and store it in app state.
        mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        async with Client(mcp_server_url) as mcp_client:
            app.state.mcp_client = mcp_client
            print(f"FastMCP client session is ready on {mcp_server_url}")
            tools = await mcp_client.list_tools()
            print("Available tools:", [tool.name for tool in tools])

            # Initialize the Gemini client and store it in app state.
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set.")
            app.state.gemini_client = genai.Client(api_key=api_key)
            print("Gemini client is ready.")
            
            # The 'yield' statement makes the clients available to the application.
            yield
            
            # This code runs on application shutdown.
            print("Clients session closed.")
    except Exception as e:
        print(f"Error during client lifespan management: {e}")
        yield