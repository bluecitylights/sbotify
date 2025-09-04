import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
from google import genai
from fastmcp import Client

# Load environment variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

gemini_client = genai.Client(api_key=api_key)

async def lifespan(app: FastAPI):
    # This block runs at application startup
    print("Initializing FastMCP client...")
    
    async with Client(os.getenv("MCP_SERVER_URL", "http://localhost:8000")) as mcp_client:
        app.state.mcp_client = mcp_client
        print("FastMCP client session is ready.")
        tools = await mcp_client.list_tools()
        print("Available tools:", [tool.name for tool in tools])  
        
        yield
        
        print("FastMCP client session closed.")

app = FastAPI(lifespan=lifespan)

fe_path = Path(__file__).parent.parent.parent / "src" / "frontend" / "index.html"

async def generate_gemini_response(prompt: str) -> str:
    """
    Generates a response from the Gemini model using the FastMCP client's session.
    """
    try:
        mcp_client = app.state.mcp_client
        async with mcp_client:
            response = await gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[mcp_client.session],
                ),

            )

            return response.text
        
    except Exception as e:
        print(f"Error calling the Gemini API with FastMCP: {e}")
        return "Sorry, I am unable to generate a response at this time."


@app.get("/")
async def serve_frontend():
    return FileResponse(fe_path)

@app.post("/chat")
async def chat_response(prompt: str = Form(...)):
    llm_response = await generate_gemini_response(prompt)
    
    return HTMLResponse(f"""
        <div class="flex justify-end">
            <div class="chat-bubble user-bubble">
                {prompt}
            </div>
        </div>
        <div class="flex justify-start">
            <div class="chat-bubble bot-bubble">
                {llm_response}
            </div>
        </div>
    """)