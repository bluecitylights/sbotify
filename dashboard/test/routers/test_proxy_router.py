import pytest
import httpx
from httpx import AsyncClient, Response, Request, RequestError, HTTPStatusError
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
import os
from src.main import app
from src.routers.proxy_router import generic_proxy

# Define a mock internal URL for testing purposes
MOCK_INTERNAL_URL = "http://mock-chat-service"

# A fixture to mock the httpx.AsyncClient. It's better to create this once.
@pytest.fixture
def mock_http_client():
    """
    Mocks the httpx.AsyncClient to control its behavior in tests.
    """
    with patch("src.routers.proxy_router.httpx.AsyncClient") as mock_client_cls:
        instance = mock_client_cls.return_value
        instance.request = AsyncMock()
        yield instance

@pytest.fixture
def mock_proxy_response():
    """
    A reusable fixture for a successful mock HTML response using MagicMock.
    This fixes the TypeError by ensuring headers.get() returns a string.
    """
    mock_html = """
    <div>
        <a hx-get="/ui/messages" id="get-data">Get Data</a>
        <form hx-post="/ui/form" hx-swap="outerHTML"></form>
        <p>This is some text.</p>
        <a href="/public-link">Public Link</a>
    </div>
    """
    mock_resp = MagicMock(spec=Response)
    mock_resp.status_code = 200
    mock_resp.text = mock_html
    mock_resp.headers = {"Content-Type": "text/html"}
    mock_resp.raise_for_status = MagicMock()
    mock_resp.iter_bytes = MagicMock(return_value=iter(mock_html.encode()))
    return mock_resp

# def test_successful_proxy_request_and_url_rewriting(mock_http_client, mock_proxy_response):
#     """
#     Tests that a request to the proxy is successful and HTMX URLs are rewritten.
#     """
#     # Arrange: Set the return value for the async request mock
#     mock_http_client.request.return_value = mock_proxy_response

#     # Patch the environment variables and SERVICE_URLS only for this test
#     with patch.dict(os.environ, {"CHAT_INTERNAL_URL": MOCK_INTERNAL_URL}), \
#             patch.dict('src.routers.proxy_router.SERVICE_URLS', {'chat': MOCK_INTERNAL_URL}):
#         # Act: Make a request to the proxy endpoint
#         client = TestClient(app)
#         response = client.get("/chat-proxy/ui/chat")

#         # Assert: Check the response status code and content
#         assert response.status_code == 200
#         assert "hx-get=\"/chat-proxy/ui/messages\"" in response.text
#         assert "hx-post=\"/chat-proxy/ui/form\"" in response.text
#         assert "href=\"/public-link\"" in response.text
#         assert mock_http_client.request.called

# def test_proxy_handles_backend_status_error(mock_http_client):
#     """
#     Tests that the proxy forwards a non-2xx status code from the backend.
#     """
#     # Arrange: Mock a 404 response from the backend
#     mock_response = MagicMock(spec=Response)
#     mock_response.status_code = 404
#     mock_response.text = "Not Found"
#     mock_response.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError(
#         "Not Found", request=Request("GET", "http://any-url.com"), response=mock_response
#     ))
#     mock_http_client.request.return_value = mock_response

#     # Patch environment for this test
#     with patch.dict(os.environ, {"CHAT_INTERNAL_URL": MOCK_INTERNAL_URL}), \
#             patch.dict('src.routers.proxy_router.SERVICE_URLS', {'chat': MOCK_INTERNAL_URL}):
#         # Act: Make a request to the proxy
#         client = TestClient(app)
#         response = client.get("/chat-proxy/ui/chat")

#         # Assert: Check that the status code is forwarded and the response body is correct
#         assert response.status_code == 404
#         assert response.text == "Not Found"

def test_proxy_handles_network_error(mock_http_client):
    """
    Tests that the proxy handles a network error (e.g., timeout, connection refused).
    """
    # Arrange: Mock a RequestError from the backend
    mock_http_client.request.side_effect = RequestError("Connection failed")

    # Patch environment for this test
    with patch.dict(os.environ, {"CHAT_INTERNAL_URL": MOCK_INTERNAL_URL}), \
            patch.dict('src.routers.proxy_router.SERVICE_URLS', {'chat': MOCK_INTERNAL_URL}):
        # Act: Make a request to the proxy
        client = TestClient(app)
        response = client.get("/chat-proxy/ui/chat")

        # Assert: Check for a 500 status code and a meaningful error message
        assert response.status_code == 500
        assert "A server error occurred." in response.text
        assert mock_http_client.request.called

def test_proxy_handles_invalid_service_name():
    """
    Tests that the proxy returns a 404 for an invalid service name.
    """
    # Act: Make a request with a non-existent service name
    client = TestClient(app)
    response = client.get("/invalid-service/ui/chat")

    # Assert: Check for a 404 Not Found error
    assert response.status_code == 404
    assert "Not Found" in response.text
