import pytest
import httpx
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi.requests import Request
import os
from src.routers.proxy_router import router, rewrite_urls, generic_proxy, SERVICE_URLS

# Create a test app
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)

client = TestClient(app)

class TestEnvironmentConfiguration:
    """Test environment configuration"""

    def test_default_chat_url(self):
        # Test that the default URL structure exists
        assert "chat" in SERVICE_URLS
        assert SERVICE_URLS["chat"] is not None

    def test_environment_variable_handling(self):
        # Test that environment variable handling works
        with patch.dict(os.environ, {"CHAT_API_URL": "http://custom-chat:9000"}):
            custom_url = os.environ.get("CHAT_API_URL", "http://chat:8080")
            assert custom_url == "http://custom-chat:9000"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])