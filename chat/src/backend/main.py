import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
from google import genai
from fastmcp import Client

# Load environment variables
# You should manage your API key securely
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

# This client is now for core Gemini API calls, not tool-calling
gemini_client = genai.Client(api_key=api_key)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing FastMCP client...")
    
    try:
        async with Client(os.getenv("MCP_SERVER_URL", "http://localhost:8000")) as mcp_client:
            app.state.mcp_client = mcp_client
            print("FastMCP client session is ready.")
            tools = await mcp_client.list_tools()
            print("Available tools:", [tool.name for tool in tools]) 
            
            yield
            
            print("FastMCP client session closed.")
    except Exception as e:
        print(f"Error during FastMCP client lifespan management: {e}")
        yield

app = FastAPI(lifespan=lifespan)

fe_path = Path(__file__).parent.parent.parent / "src" / "frontend" / "index.html"

async def generate_gemini_response(prompt: str) -> str:
    """
    Generates a response from the Gemini model using the FastMCP client's session.
    """
    try:
        mcp_client = app.state.mcp_client
        
        system_instruction = "You are a helpful AI assistant. Answer general knowledge questions using your own knowledge. Only use the provided tools when the question explicitly requires their functionality, such as performing a calculation or accessing specific external data."
        
        response = await gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[mcp_client.session],
                    system_instruction=system_instruction,
                ),

            )

        is_tool_based = bool(response.automatic_function_calling_history)
        
        response_text = ""
        if response.text:
            response_text = response.text

        # Add a prefix if a tool was used.
        if is_tool_based:
            return f"Tool-based: {response_text}"
        else:
            return response_text
        
    except Exception as e:
        print(f"Error calling the Gemini API with FastMCP: {e}")
        return "Sorry, I am unable to generate a response at this time."


@app.get("/")
async def serve_frontend():
    return FileResponse(fe_path)

@app.get("/tools")
async def get_available_tools():
    """
    Fetches and returns the list of available tools from the MCP server.
    """
    try:
        mcp_client = app.state.mcp_client
        tools = await mcp_client.list_tools()
        tool_names = [tool.name for tool in tools]
        
        if not tool_names:
            return HTMLResponse("<p class='tools-error'>No tools available.</p>")

        html_content = "<div class='flex gap-2 flex-wrap'>"
        for tool_name in tool_names:
            html_content += f"<span class='tool-badge'>{tool_name}</span>"
        html_content += "</div>"
        
        return HTMLResponse(html_content)
        
    except Exception as e:
        print(f"Error fetching available tools: {e}")
        return HTMLResponse("<p class='tools-error'>Failed to load tools.</p>")


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
