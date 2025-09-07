import asyncio
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastmcp import Client
from pathlib import Path
from ..dependencies import get_mcp_client

# Get the base directory of the project to locate the templates folder
BASE_DIR = Path(__file__).resolve().parent

# Initialize the Jinja2Templates instance, pointing to the 'ui' directory
templates = Jinja2Templates(directory=BASE_DIR)

router = APIRouter()

@router.get("/tools", response_class=HTMLResponse)
async def get_available_resources(request: Request, mcp_client: Client = Depends(get_mcp_client)):
    """
    Fetches available tools, resources, and prompts from the MCP server
    and renders them using an HTML template.
    """
    try:
        # Fetch all three types of objects concurrently
        tools_list, resources_list, prompts_list = await asyncio.gather(
            mcp_client.list_tools(),
            mcp_client.list_resources(),
            mcp_client.list_prompts()
        )
        
        # Render the 'tools.html' template with the fetched data
        # The 'request' object is required for Jinja2 templates
        return templates.TemplateResponse(
            "tools.html",
            {
                "request": request,
                "tools_list": tools_list,
                "resources_list": resources_list,
                "prompts_list": prompts_list,
            }
        )
        
    except Exception as e:
        print(f"Error fetching available resources: {e}")
        return HTMLResponse("<p class='tools-error text-sm text-gray-500'>Failed to load resources.</p>")
