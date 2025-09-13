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


class TestGenericProxySync:
    """Test the generic proxy function with synchronous wrappers"""

    def create_mock_request(self, method="GET", headers=None, query_params=None, body=b""):
        """Helper to create mock request objects"""
        if headers is None:
            headers = {"user-agent": "test-agent", "host": "localhost"}
        if query_params is None:
            query_params = {}
            
        request = Mock(spec=Request)
        request.method = method
        request.headers = headers
        request.query_params = query_params
        
        # Create an async mock for body()
        async_body_mock = AsyncMock(return_value=body)
        request.body = async_body_mock
        
        return request

    def test_service_not_found_sync(self):
        """Test service not found error"""
        request = self.create_mock_request()
        
        # Use a sync test by checking the function behavior
        # We know generic_proxy should raise HTTPException for unknown services
        import asyncio
        
        async def run_test():
            with pytest.raises(HTTPException) as exc_info:
                await generic_proxy("nonexistent", "path", request)
            assert exc_info.value.status_code == 404
            assert "Service not found" in str(exc_info.value.detail)
        
        asyncio.run(run_test())

    @patch('src.routers.proxy_router.httpx.AsyncClient')
    def test_successful_html_response_sync(self, mock_client):
        """Test successful HTML response"""
        request = self.create_mock_request()
        
        # Mock the HTTP client response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<div hx-get="/api/data">Content</div>'
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_response.raise_for_status = Mock()

        # Configure the async client mock
        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

        import asyncio
        
        async def run_test():
            result = await generic_proxy("chat", "api/data", request)
            # Verify the response was rewritten
            assert 'hx-get="/chat-proxy/api/data"' in result.body.decode()
            assert result.status_code == 200
        
        asyncio.run(run_test())

    @patch('src.routers.proxy_router.httpx.AsyncClient')
    def test_successful_json_response_sync(self, mock_client):
        """Test successful JSON response"""
        request = self.create_mock_request()
        
        # Mock the HTTP client response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"key": "value"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.raise_for_status = Mock()

        # Configure the async client mock
        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

        import asyncio
        
        async def run_test():
            result = await generic_proxy("chat", "api/data", request)
            # Verify the response was not rewritten (non-HTML)
            assert result.body == b'{"key": "value"}'
            assert result.status_code == 200
        
        asyncio.run(run_test())

    @patch('src.routers.proxy_router.httpx.AsyncClient')
    def test_http_status_error_sync(self, mock_client):
        """Test HTTP status error handling"""
        request = self.create_mock_request()
        
        # Mock the HTTP client to raise an HTTPStatusError
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        
        error = httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        
        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(side_effect=error)
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

        import asyncio
        
        async def run_test():
            with pytest.raises(HTTPException) as exc_info:
                await generic_proxy("chat", "api/data", request)
            
            assert exc_info.value.status_code == 404
            assert "Backend service returned an error" in str(exc_info.value.detail)
        
        asyncio.run(run_test())

    @patch('src.routers.proxy_router.httpx.AsyncClient')
    def test_request_error_sync(self, mock_client):
        """Test request error handling"""
        request = self.create_mock_request()
        
        # Mock the HTTP client to raise a RequestError
        error = httpx.RequestError("Connection failed")
        
        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(side_effect=error)
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

        import asyncio
        
        async def run_test():
            with pytest.raises(HTTPException) as exc_info:
                await generic_proxy("chat", "api/data", request)
            
            assert exc_info.value.status_code == 503
            assert "Could not connect to backend service" in str(exc_info.value.detail)
        
        asyncio.run(run_test())

if __name__ == "__main__":
    pytest.main([__file__, "-v"])