# tests/ui/test_ui_tools.py

import pytest
from fastapi.testclient import TestClient

# The test function. Note that no fixtures are defined here;
# they are all provided by conftest.py.
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
    
    # Verify the headings are present.
    assert "<h3>Available Tools</h3>" in html_content
    assert "<h3>Available Resources</h3>" in html_content
    assert "<h3>Available Prompts</h3>" in html_content
    
    # Verify that the mocked tool, resource, and prompt names are in the HTML.
    # assert '<span class="tool-badge">mock_tool</span>' in html_content
    # assert '<span class="resource-badge">mock_resource</span>' in html_content
    # assert '<span class="prompt-badge">mock_prompt</span>' in html_content