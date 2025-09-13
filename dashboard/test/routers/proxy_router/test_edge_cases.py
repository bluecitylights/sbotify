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

class TestComplexScenarios:
    """Test complex real-world scenarios"""

    def test_complex_html_rewriting(self):
        sample_html = '''
        <html>
            <body>
                <div hx-get="/api/data" hx-post="/api/submit">
                    <a href="/page">Link</a>
                    <img src="/image.jpg" alt="test">
                    <form action="/form-submit">
                        <input type="submit" value="Submit">
                    </form>
                </div>
            </body>
        </html>
        '''
        
        result = rewrite_urls(sample_html, "chat")
        
        assert 'hx-get="/chat-proxy/api/data"' in result
        assert 'hx-post="/chat-proxy/api/submit"' in result
        assert 'href="/chat-proxy/page"' in result
        assert 'src="/chat-proxy/image.jpg"' in result
        assert 'action="/chat-proxy/form-submit"' in result

    def test_malformed_html_handling(self):
        # Test that malformed HTML doesn't break the rewriting
        malformed_html = '<div hx-get="/api" class="test"<a href="/page">Link</div>'
        result = rewrite_urls(malformed_html, "chat")
        # Should still rewrite valid URLs even with malformed HTML
        assert 'hx-get="/chat-proxy/api"' in result
        assert 'href="/chat-proxy/page"' in result

    def test_large_response_handling(self):
        # Test handling of large HTML responses
        large_html = '<div hx-get="/api/data">Content</div>' * 1000
        result = rewrite_urls(large_html, "chat")
        # Should rewrite all instances
        assert result.count('hx-get="/chat-proxy/api/data"') == 1000

    def test_edge_case_url_patterns(self):
        # Test various edge cases
        html = '''
        <div hx-get="/api/data?param=value&other=test">
            <a href="/complex/path/with-dashes_and_underscores/123">
            <img src="/images/file.name.with.dots.jpg">
        </div>
        '''
        result = rewrite_urls(html, "service")
        
        assert 'hx-get="/service-proxy/api/data?param=value&other=test"' in result
        assert 'href="/service-proxy/complex/path/with-dashes_and_underscores/123"' in result
        assert 'src="/service-proxy/images/file.name.with.dots.jpg"' in result


# Pytest fixtures for common test data
@pytest.fixture
def sample_html():
    return '''
    <html>
        <body>
            <div hx-get="/api/data" hx-post="/api/submit">
                <a href="/page">Link</a>
                <img src="/image.jpg" alt="test">
                <form action="/form-submit">
                    <input type="submit" value="Submit">
                </form>
            </div>
        </body>
    </html>
    '''


if __name__ == "__main__":
    pytest.main([__file__, "-v"])