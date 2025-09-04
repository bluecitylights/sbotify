# A simple FastAPI application to act as a Backend for Frontend (BFF).
# To run this file, you'll need to install FastAPI and a server like Uvicorn:
# uv add fastapi uvicorn google-generativeai

import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import google.generativeai as genai

# Load environment variables. Uvicorn will automatically handle this
# if you run it with the --env-file flag, e.g.:
# uvicorn bff_app:app --reload --env-file example.env
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

# Configure the Gemini API client
genai.configure(api_key=api_key)

app = FastAPI()

fe_path = Path(__file__).parent.parent.parent / "src" / "index.html"

# An async function to get a response from the Gemini model
async def generate_gemini_response(prompt: str) -> str:
    """
    Generates a response from the Gemini model based on the user's prompt.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = await model.generate_content_async(prompt)
        # Ensure the response is not empty before returning
        if response and response.text:
            return response.text
        else:
            return "No response received from the AI."
    except Exception as e:
        print(f"Error calling the Gemini API: {e}")
        return "Sorry, I am unable to generate a response at this time."

@app.get("/")
async def serve_frontend():
    return FileResponse(fe_path)

@app.post("/chat")
async def chat_response(prompt: str = Form(...)):
    llm_response = await generate_gemini_response(prompt)
    
    # Return the HTML fragment that HTMX will swap into the page.
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

# To run the server, use the command:
# uvicorn bff_app:app --reload --env-file example.env
