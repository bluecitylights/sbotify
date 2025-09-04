# dependencies.py
from fastapi import Request
from google import genai
from fastmcp import Client

def get_gemini_client(request: Request) -> genai.Client:
    return request.app.state.gemini_client

def get_mcp_client(request: Request) -> Client:
    return request.app.state.mcp_client