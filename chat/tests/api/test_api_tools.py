# tests/api/test_api_tools.py

import pytest

def test_get_available_tools_json(test_client):
    """Tests the /api/tools endpoint."""
    response = test_client.get("/api/tools")
    
    assert response.status_code == 200
    assert response.json() == {
        "tools": ["mock_tool"],
        "resources": ["mock_resource"],
        "prompts": ["mock_prompt"]
    }