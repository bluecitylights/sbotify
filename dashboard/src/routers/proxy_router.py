import os
import re
import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

router = APIRouter()

# Service URLs are stored as environment variables for a real deployment.
# We'll use a dictionary for development and testing.
SERVICE_URLS = {
    "chat": os.getenv("CHAT_INTERNAL_URL", "http://chat-service:8000"),
    # Add other services here as needed
}

def rewrite_urls(html_content: str, service_name: str) -> str:
    """
    Rewrites relative URLs in HTMX attributes and standard hrefs to point to the proxy endpoint.
    This ensures that subsequent requests from the front-end are routed correctly.
    """
    # Pattern to find hx-get, hx-post, hx-put, hx-delete attributes with relative URLs
    hx_pattern = re.compile(r'hx-(get|post|put|delete)="(/[^"]*)"')
    rewritten_html = hx_pattern.sub(rf'hx-\1="/{service_name}-proxy\2"', html_content)

    # Pattern to find standard href attributes with relative URLs
    href_pattern = re.compile(r'href="(/[^"]*)"')
    rewritten_html = href_pattern.sub(rf'href="/{service_name}-proxy\1"', rewritten_html)
    
    return rewritten_html

@router.api_route("/{service}-proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
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
        async with httpx.AsyncClient() as client:
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
            rewritten_html = rewrite_urls(proxy_response.text, service)
            return HTMLResponse(content=rewritten_html, status_code=proxy_response.status_code)

        # For non-HTML responses, stream the content directly
        return StreamingResponse(
            content=proxy_response.iter_bytes(),
            status_code=proxy_response.status_code,
            headers=proxy_response.headers
        )

    except httpx.RequestError as e:
        print(f"An error occurred while proxying the request to {target_url}: {e}")
        raise HTTPException(status_code=500, detail="A server error occurred.")
