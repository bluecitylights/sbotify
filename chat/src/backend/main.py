import os
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Initialize FastAPI
app = FastAPI()

# Mount the static files directory to serve your front-end assets (e.g., CSS)
# The `os.path.dirname(__file__)` gets the directory of the current file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FE_PATH = os.path.join(BASE_DIR, '..', 'frontend')
app.mount("/static", StaticFiles(directory=FE_PATH), name="static")

# We will use Jinja2 to serve the HTML file
templates = Jinja2Templates(directory=FE_PATH)

# Route to serve the main HTML page
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route to handle the chat messages. This is a POST request from the form.
@app.post("/chat", response_class=HTMLResponse)
async def chat_response(request: Request):
    # This is a placeholder for the actual LLM call.
    # We will get the user's prompt from the form data.
    form_data = await request.form()
    prompt = form_data.get("prompt")
    llm_response = f"Hello! The server received your message: '{prompt}'."
    
    # Return the HTML for the new chat bubble
    return f"""
    <div class="flex justify-end">
        <div class="chat-bubble user-bubble rounded-xl rounded-br-none p-3 shadow-md">
            {prompt}
        </div>
    </div>
    <div class="flex justify-start">
        <div class="chat-bubble bot-bubble rounded-xl rounded-bl-none p-3 shadow-md">
            {llm_response}
        </div>
    </div>
    """

# Run the server directly from this file
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
