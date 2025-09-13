import httpx
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import HTMLResponse
import logging
import os
import re

# Set up basic logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This is an example of an internal service, not exposed to the public internet.
# In a real-world scenario, this might be a private URL or an internal Docker service name.
CHAT_INTERNAL_URL = os.environ.get("CHAT_API_URL", "http://chat:8080")

SERVICE_URLS = {
    "chat": CHAT_INTERNAL_URL,
}

router = APIRouter()

def rewrite_urls(html_content: str, service: str) -> str:
    """
    Rewrites relative URLs in HTMX and standard HTML attributes to use the proxy path.
    """
    proxy_prefix = f"/{service}-proxy"
    
    # Regex to find URLs in hx-get, hx-post, href, src, and action attributes
    # The regex is non-greedy, so it finds the shortest match for the URL.
    rewritten_content = re.sub(
        r'(hx-get|hx-post|hx-put|hx-delete|hx-patch|hx-swap-oob|href|src|action)=(["\'])(/.*?)["\']',
        lambda m: f'{m.group(1)}={m.group(2)}{proxy_prefix}{m.group(3)}{m.group(2)}',
        html_content
    )
    return rewritten_content

@router.get("/{service}-proxy/{path:path}")
@router.post("/{service}-proxy/{path:path}")
async def generic_proxy(service: str, path: str, request: Request):
    """
    Generic proxy endpoint that forwards a request to the appropriate backend service,
    rewrites HTMX and other relative URLs in the response HTML, and streams the response back.
    """
    if service not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail="Service not found")

    base_url = SERVICE_URLS[service]
    target_url = f"{base_url}/{path}"

    headers = {key: value for key, value in request.headers.items() if key.lower() not in ["host", "authorization"]}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            proxy_response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=await request.body()
            )
            proxy_response.raise_for_status()
            
            # Rewrite HTMX and other URLs if the response is HTML
            content_type = proxy_response.headers.get("Content-Type", "")
            if "text/html" in content_type:
                html_content = proxy_response.text
                rewritten_content = rewrite_urls(html_content, service)
                return HTMLResponse(content=rewritten_content, status_code=proxy_response.status_code)
            
            # For non-HTML content, return the response directly
            return Response(content=proxy_response.content, status_code=proxy_response.status_code, headers=proxy_response.headers)

    except httpx.HTTPStatusError as e:
        logger.error(f"Backend service returned an error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Backend service returned an error: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Could not connect to backend service: {e}")
        raise HTTPException(status_code=503, detail=f"Could not connect to backend service: {e}")
