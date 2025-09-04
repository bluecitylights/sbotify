import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

from .lifespan import lifespan

from .api.chat import router as chat_router
from .api.tools import router as tools_router


app = FastAPI(lifespan=lifespan)

# Add the API routers with prefixes to separate them from the UI
app.include_router(chat_router, prefix="/api")
app.include_router(tools_router, prefix="/api")

# Assuming this path is correct for your project structure
fe_path = Path(__file__).parent.parent.parent / "src" / "frontend" / "index.html"

@app.get("/")
async def serve_frontend_root():
    return FileResponse(fe_path)
