from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastmcp import Client
from ..dependencies import get_mcp_client
import asyncio

router = APIRouter()

@router.get("/tools")
async def get_available_resources(mcp_client: Client = Depends(get_mcp_client)):
    """
    Fetches and returns a list of available tools, resources, and prompts from the MCP server.
    """
    try:
        # Fetch all three types of objects concurrently
        tools_list, resources_list, prompts_list = await asyncio.gather(
            mcp_client.list_tools(),
            mcp_client.list_resources(),
            mcp_client.list_prompts()
        )
        
        html_content = ""

        if tools_list:
            html_content += "<h3>Available Tools</h3>"
            html_content += "<div class='flex gap-2 flex-wrap'>"
            for tool in tools_list:
                html_content += f"<span class='tool-badge'>{tool.name}</span>"
            html_content += "</div>"

        if resources_list:
            html_content += "<h3>Available Resources</h3>"
            html_content += "<div class='flex gap-2 flex-wrap'>"
            for resource in resources_list:
                html_content += f"<span class='resource-badge'>{resource.name}</span>"
            html_content += "</div>"
        
        if prompts_list:
            html_content += "<h3>Available Prompts</h3>"
            html_content += "<div class='flex gap-2 flex-wrap'>"
            for prompt in prompts_list:
                html_content += f"<span class='prompt-badge'>{prompt.name}</span>"
            html_content += "</div>"

        if not (tools_list or resources_list or prompts_list):
            return HTMLResponse("<p class='tools-error'>No resources, tools, or prompts available.</p>")

        return HTMLResponse(html_content)
        
    except Exception as e:
        print(f"Error fetching available resources: {e}")
        return HTMLResponse("<p class='tools-error'>Failed to load resources.</p>")