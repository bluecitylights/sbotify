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


class TestRewriteUrls:
    """Test the URL rewriting function"""

    def test_rewrite_hx_get_urls(self):
        html = '<div hx-get="/api/data">Content</div>'
        expected = '<div hx-get="/chat-proxy/api/data">Content</div>'
        result = rewrite_urls(html, "chat")
        assert result == expected

    def test_rewrite_hx_post_urls(self):
        html = '<form hx-post="/submit">Content</form>'
        expected = '<form hx-post="/chat-proxy/submit">Content</form>'
        result = rewrite_urls(html, "chat")
        assert result == expected

    def test_rewrite_multiple_hx_attributes(self):
        html = '''
        <div hx-get="/api/get" hx-post="/api/post" hx-put="/api/put" 
             hx-delete="/api/delete" hx-patch="/api/patch">Content</div>
        '''
        result = rewrite_urls(html, "chat")
        assert 'hx-get="/chat-proxy/api/get"' in result
        assert 'hx-post="/chat-proxy/api/post"' in result
        assert 'hx-put="/chat-proxy/api/put"' in result
        assert 'hx-delete="/chat-proxy/api/delete"' in result
        assert 'hx-patch="/chat-proxy/api/patch"' in result

    def test_rewrite_href_urls(self):
        html = '<a href="/page">Link</a>'
        expected = '<a href="/chat-proxy/page">Link</a>'
        result = rewrite_urls(html, "chat")
        assert result == expected

    def test_rewrite_src_urls(self):
        html = '<img src="/image.jpg" alt="image">'
        expected = '<img src="/chat-proxy/image.jpg" alt="image">'
        result = rewrite_urls(html, "chat")
        assert result == expected

    def test_rewrite_action_urls(self):
        html = '<form action="/submit">Content</form>'
        expected = '<form action="/chat-proxy/submit">Content</form>'
        result = rewrite_urls(html, "chat")
        assert result == expected

    def test_rewrite_with_single_quotes(self):
        html = "<div hx-get='/api/data'>Content</div>"
        expected = "<div hx-get='/chat-proxy/api/data'>Content</div>"
        result = rewrite_urls(html, "chat")
        assert result == expected

    def test_rewrite_complex_paths(self):
        html = '<div hx-get="/api/v1/users/123/posts">Content</div>'
        expected = '<div hx-get="/chat-proxy/api/v1/users/123/posts">Content</div>'
        result = rewrite_urls(html, "chat")
        assert result == expected

    def test_no_rewrite_external_urls(self):
        html = '<a href="https://example.com">Link</a>'
        result = rewrite_urls(html, "chat")
        assert result == html  # Should remain unchanged

    def test_no_rewrite_relative_urls_without_slash(self):
        html = '<a href="page.html">Link</a>'
        result = rewrite_urls(html, "chat")
        assert result == html  # Should remain unchanged

    def test_different_service_name(self):
        html = '<div hx-get="/api/data">Content</div>'
        expected = '<div hx-get="/auth-proxy/api/data">Content</div>'
        result = rewrite_urls(html, "auth")
        assert result == expected

    def test_multiple_urls_in_same_html(self):
        html = '''
        <div hx-get="/api/data">
            <a href="/page">Link</a>
            <img src="/image.jpg">
        </div>
        '''
        result = rewrite_urls(html, "chat")
        assert 'hx-get="/chat-proxy/api/data"' in result
        assert 'href="/chat-proxy/page"' in result
        assert 'src="/chat-proxy/image.jpg"' in result

    def test_hx_swap_oob_rewriting(self):
        html = '<div hx-swap-oob="/target">Content</div>'
        expected = '<div hx-swap-oob="/chat-proxy/target">Content</div>'
        result = rewrite_urls(html, "chat")
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])