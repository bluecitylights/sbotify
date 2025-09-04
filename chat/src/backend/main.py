import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

from .lifespan import lifespan

from .api import api_router
from .ui import ui_router

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api")
app.include_router(ui_router, prefix="/ui")

fe_path = Path(__file__).parent.parent.parent / "src" / "frontend" / "index.html"

@app.get("/")
async def serve_frontend_root():
    return FileResponse(fe_path)
