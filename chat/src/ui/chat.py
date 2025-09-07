import os
from fastapi import APIRouter, Form, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastmcp import Client
from pathlib import Path
from google import genai
from ..dependencies import get_mcp_client, get_gemini_client
from ..services.llm_service import generate_gemini_response

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent

@router.get("/chat", response_class=HTMLResponse)
async def get_chat_fragment():
    """
    Returns the core chat application HTML fragment for HTMX loading by
    reading the contents of the chat.html file.
    """
    # Construct the path to the chat.html file
    file_path = BASE_DIR / "ui" / "chat.html"
    
    # Read the file and return its content as an HTMLResponse
    return HTMLResponse(content=file_path.read_text(), status_code=200)

@router.post("/chat")
async def chat_response(
    prompt: str = Form(...),
    gemini_client: genai.Client = Depends(get_gemini_client),
    mcp_client: Client = Depends(get_mcp_client)
):
    # This is an async generator, so we can't just 'await' it.
    response_stream = generate_gemini_response(prompt, gemini_client, mcp_client)

    # Use a local async generator to format the HTML response chunks
    async def chat_streamer():
        yield f"""
        <div class="flex justify-end">
            <div class="chat-bubble user-bubble">
                {prompt}
            </div>
        </div>
        <div class="flex justify-start">
            <div class="chat-bubble bot-bubble">
        """
        async for chunk in response_stream:
            # Yield each text chunk from the Gemini stream
            yield chunk

        yield f"""
            </div>
        </div>
        """

    # Return a StreamingResponse with the HTML content type
    return StreamingResponse(chat_streamer(), media_type="text/html")
