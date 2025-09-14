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

class TestIntegrationWithTestClient:
    """Integration tests using FastAPI TestClient"""

    @patch('src.routers.proxy_router.httpx.AsyncClient')
    def test_get_request_integration(self, mock_client):
        # Mock the HTTP client response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<div hx-get="/api/test">Hello World</div>'
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.raise_for_status = Mock()

        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

        response = client.get("/chat-proxy/api/test")
        
        assert response.status_code == 200
        assert 'hx-get="/chat-proxy/api/test"' in response.text

    @patch('src.routers.proxy_router.httpx.AsyncClient')
    def test_post_request_integration(self, mock_client):
        # Mock the HTTP client response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"success": true}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.raise_for_status = Mock()

        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

        response = client.post("/chat-proxy/api/submit", json={"data": "test"})
        
        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_invalid_service_integration(self):
        response = client.get("/invalid-proxy/api/test")
        assert response.status_code == 404
        assert "Service not found" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])