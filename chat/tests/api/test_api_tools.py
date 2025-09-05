# tests/api/test_api_tools.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastmcp.tools import Tool
from fastmcp.resources import Resource
from fastmcp.prompts import Prompt
from src.main import app
from src.dependencies import get_mcp_client

@pytest.fixture(autouse=True)
def override_dependencies():
    mock_client = AsyncMock() 
    
    mock_client.list_tools.return_value = [
        Tool(
            name="mock_tool",
            parameters={"param_name": {"type": "string", "description": "test param"}}
        )
    ]
    mock_resource = MagicMock()
    mock_resource.name = "mock_resource"
    mock_client.list_resources.return_value = [mock_resource]

    mock_prompt = MagicMock()
    mock_prompt.name = "mock_prompt"

    mock_client.list_prompts.return_value = [mock_prompt]
    
    app.dependency_overrides[get_mcp_client] = lambda: mock_client
    
    yield
    
    app.dependency_overrides.clear()

# The actual test function
def test_get_available_tools_json(test_client):
    """
    Tests the /api/tools endpoint to ensure it returns the correct JSON response.
    The test_client fixture is provided by the shared conftest.py file.
    """
    response = test_client.get("/api/tools")

    # Assert that the status code is 200 OK
    assert response.status_code == 200

    # Assert that the JSON response matches the data returned by our mock client
    assert response.json() == {
        "tools": ["mock_tool"],
        "resources": ["mock_resource"],
        "prompts": ["mock_prompt"]
    }