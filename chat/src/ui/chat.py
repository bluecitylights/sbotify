import os
from fastapi import APIRouter, Form, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastmcp import Client
from google import genai
from ..dependencies import get_mcp_client, get_gemini_client
from ..services.llm_service import generate_gemini_response


import os

router = APIRouter()

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