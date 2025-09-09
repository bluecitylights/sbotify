from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.routers import proxy_router
import os
import httpx
import uvicorn
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the base directory for the application
BASE_DIR = Path(__file__).parent.parent

# Initialize the FastAPI app
app = FastAPI(
    title="Sbotify Dashboard",
    description="A microservice-based dashboard for Sbotify.",
    version="0.1.0",
)

# --- Configuration from Environment Variables ---
CHAT_API_URL = os.environ.get("CHAT_API_URL", "http://127.0.0.1:8080")

# --- HTML Fragments for each "app" ---
# Note: This is now just a placeholder for the dummy project
dummy_project_fragment = """
<div class="p-6">
    <h2 class="text-2xl font-semibold text-gray-800 mb-4">Dummy Project</h2>
    <div class="bg-white p-4 rounded-lg shadow-md">
        <p class="text-gray-600">This content is from the "Dummy Project" endpoint. It's a simple example of how to load dynamic text content into the dashboard panel using HTMX.</p>
    </div>
</div>
"""

# Create the static directory if it doesn't exist
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)

# Mount the static files directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include the proxy router
app.include_router(proxy_router, tags=["Proxy"])

@app.get("/", response_class=HTMLResponse, name="main_dashboard")
async def main_dashboard(request: Request):
    """
    Serves the main dashboard HTML page.
    """
    html_file_path = BASE_DIR / "src" / "index.html"
    logger.info(f"Looking for index.html at: {html_file_path.absolute()}")
    if not html_file_path.is_file():
        logger.error(f"File not found: {html_file_path}")
        raise HTTPException(status_code=500, detail="Internal server error: index.html not found.")
    
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)

@app.get("/chat", response_class=HTMLResponse)
async def get_chat_app():
    """
    Connects to the chat server to fetch the chat application HTML fragment.
    """
    # Define the URL of your chat API server.
    chat_api_url = f"{CHAT_API_URL}/ui/chat"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(chat_api_url)
            response.raise_for_status()
            return HTMLResponse(content=response.text, status_code=response.status_code)
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Status Error: {e.response.status_code} - {e.response.text}")
        return HTMLResponse(
            f"Error from chat server: {e.response.status_code}",
            status_code=e.response.status_code
        )
    except httpx.ConnectError as e:
        logger.error(f"Connection Error: {e}")
        return HTMLResponse(
            f"Connection failed: Could not connect to chat server.",
            status_code=500
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return HTMLResponse(
            "An unexpected error occurred while fetching the chat app.",
            status_code=500
        )


@app.get("/dummy-project", response_class=HTMLResponse)
async def get_dummy_project_app():
    """Returns the HTML fragment for the dummy project."""
    return HTMLResponse(content=dummy_project_fragment)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
