from fastapi import APIRouter, Depends
from typing import Dict, List
from fastmcp import Client
from ..dependencies import get_mcp_client

router = APIRouter()

@router.get("/tools")
async def get_available_tools_json(mcp_client: Client = Depends(get_mcp_client)) -> Dict[str, List[str]]:
    """
    Fetches and returns the list of available tools, resources, and prompts from the MCP server in JSON format.
    """
    tools = await mcp_client.list_tools()
    resources = await mcp_client.list_resources()
    prompts = await mcp_client.list_prompts()
    
    return {
        "tools": [tool.name for tool in tools],
        "resources": [resource.name for resource in resources],
        "prompts": [prompt.name for prompt in prompts]
    }