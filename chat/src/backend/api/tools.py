from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastmcp import Client
from ..dependencies import get_mcp_client

router = APIRouter()

@router.get("/tools")
async def get_available_tools(mcp_client: Client = Depends(get_mcp_client)):
    """
    Fetches and returns a list of available tools, resources, and prompts from the MCP server.
    """
    try:
        # Fetch all three types of objects
        tools = await mcp_client.list_tools()
        resources = await mcp_client.list_resources()
        prompts = await mcp_client.list_prompts()
        
        tool_names = [tool.name for tool in tools]
        resource_names = [resource.name for resource in resources]
        prompt_names = [prompt.name for prompt in prompts]
        
        # Build the HTML content
        html_content = ""
        
        if tool_names:
            html_content += "<h4>Tools:</h4>"
            html_content += "<div class='flex gap-2 flex-wrap'>"
            for name in tool_names:
                html_content += f"<span class='tool-badge'>{name}</span>"
            html_content += "</div>"
        
        if resource_names:
            html_content += "<h4>Resources:</h4>"
            html_content += "<div class='flex gap-2 flex-wrap'>"
            for name in resource_names:
                html_content += f"<span class='resource-badge'>{name}</span>"
            html_content += "</div>"
            
        if prompt_names:
            html_content += "<h4>Prompts:</h4>"
            html_content += "<div class='flex gap-2 flex-wrap'>"
            for name in prompt_names:
                html_content += f"<span class='prompt-badge'>{name}</span>"
            html_content += "</div>"
            
        if not (tool_names or resource_names or prompt_names):
            return HTMLResponse("<p class='tools-error'>No resources, tools, or prompts available.</p>")

        return HTMLResponse(html_content)
        
    except Exception as e:
        print(f"Error fetching available resources: {e}")
        return HTMLResponse("<p class='tools-error'>Failed to load resources.</p>")