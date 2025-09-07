import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .lifespan import lifespan

from .api import api_router
from .ui import ui_router

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api")
app.include_router(ui_router, prefix="/ui")

# Mount the static directory from the project root.
app.mount("/static", StaticFiles(directory="../static"), name="static")

# fe_path = Path(__file__).parent.parent / "ui" / "index.html"
fe_path = Path(__file__).parent / "ui" / "index.html"

@app.get("/")
async def serve_frontend_root():
    return FileResponse(fe_path)
