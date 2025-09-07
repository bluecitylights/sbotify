import os
import uvicorn
import httpx
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException

# Create the FastAPI app instance
app = FastAPI()

# Create a new router to handle requests that will be proxied
ui_router = APIRouter()

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

# --- Main Dashboard Routes ---

try:
    # This path is correct for the Docker container.
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # If the above path fails, we assume we are in local development
    # where the static directory is one level up.
    app.mount("/static", StaticFiles(directory="../static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def main_dashboard():
    """Serves the main dashboard HTML page."""
    with open("index.html", "r") as f:
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
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            # Return the content received from the chat server
            return HTMLResponse(content=response.text, status_code=response.status_code)
    except httpx.HTTPStatusError as e:
        # Handle HTTP status errors (e.g., 404, 500)
        return HTMLResponse(f"Error connecting to chat server: {e}", status_code=e.response.status_code)
    except httpx.RequestError as e:
        # Handle general request errors (e.g., network issues, server not running)
        return HTMLResponse(f"Request failed: {e}", status_code=500)


@app.get("/dummy-project", response_class=HTMLResponse)
async def get_dummy_project_app():
    """Returns the HTML fragment for the dummy project."""
    return HTMLResponse(content=dummy_project_fragment)


# --- Proxy Route for HTMX Requests from the Chat Fragment ---
# This will catch all requests with the "/ui" prefix and forward them
# to the appropriate endpoint on the chat server.
@ui_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_ui_requests(request: Request, path: str):
    """Proxies all requests with a /ui prefix to the chat server."""
    # The base URL of the chat server's UI endpoints
    chat_ui_base_url = f"{CHAT_API_URL}/ui"
    proxy_url = f"{chat_ui_base_url}/{path}"

    try:
        async with httpx.AsyncClient() as client:
            # Reconstruct headers and body from the incoming request
            headers = {name: value for name, value in request.headers.items() if name.lower() not in ("host", "authorization")}
            body = await request.body()

            # Forward the request to the chat server
            proxy_response = await client.request(
                method=request.method,
                url=proxy_url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            proxy_response.raise_for_status()

            # Return the response from the chat server
            return HTMLResponse(
                content=proxy_response.text,
                status_code=proxy_response.status_code,
                headers=dict(proxy_response.headers)
            )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Proxy error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Proxy request failed: {e}")


# Mount the new router to the main app with the "/ui" prefix
app.mount("/ui", ui_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
