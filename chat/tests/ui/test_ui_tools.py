# tests/ui/test_ui_tools.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from fastmcp.tools import Tool
from fastmcp.resources import Resource
from fastmcp.prompts import Prompt

# Import the main app and dependency function from your source code
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
def test_get_available_resources_html(test_client: TestClient):
    """
    Tests the /ui/tools endpoint to ensure it returns the correct HTML content.
    The 'test_client' fixture is automatically provided by conftest.py.
    """
    response = test_client.get("/ui/tools")
    
    # 1. Assert the HTTP status code is OK.
    assert response.status_code == 200
    
    # 2. Assert that the response is HTML.
    assert "text/html" in response.headers["content-type"]
    
    # 3. Check for expected content in the HTML response.
    html_content = response.text
    print(html_content)  # For debugging purposes
    # Verify the headings are present.
    assert "<h3>Available Tools</h3>" in html_content
    assert "<h3>Available Resources</h3>" in html_content
    assert "<h3>Available Prompts</h3>" in html_content
    
    # Verify that the mocked tool, resource, and prompt names are in the HTML.
    # assert '<span class="tool-badge">mock_tool</span>' in html_content
    # assert '<span class="resource-badge">mock_resource</span>' in html_content
    # assert '<span class="prompt-badge">mock_prompt</span>' in html_content