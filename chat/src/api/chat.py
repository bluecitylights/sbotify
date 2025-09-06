from fastapi import APIRouter, Form, Depends
from fastapi.responses import StreamingResponse
from fastmcp import Client
from google import genai
from ..dependencies import get_mcp_client, get_gemini_client
from ..services.llm_service import generate_gemini_response

router = APIRouter()

@router.post("/chat")
async def chat_response_stream(
    prompt: str = Form(...),
    gemini_client: genai.Client = Depends(get_gemini_client),
    mcp_client: Client = Depends(get_mcp_client)
):
    response_stream = generate_gemini_response(prompt, gemini_client, mcp_client)
    return StreamingResponse(response_stream, media_type="text/plain")