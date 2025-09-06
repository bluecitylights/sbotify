# tests/conftest.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

# Import from your application
from src.main import app
from src.dependencies import get_mcp_client
from fastmcp.tools import Tool
from fastmcp.resources import Resource
from fastmcp.prompts import Prompt

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

# The test client fixture
@pytest.fixture(scope="session")
def test_client():
    """Provides a TestClient for testing FastAPI endpoints."""
    with TestClient(app) as client:
        yield client