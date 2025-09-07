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

# --- Dynamic Path Resolution for Static Files ---
# We try the production path first, as that is the intended final environment.
# The local development path becomes the fallback.
try:
    # This path is correct for the Docker container.
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # If the above path fails, we assume we are in local development
    # where the static directory is one level up.
    app.mount("/static", StaticFiles(directory="../static"), name="static")

# fe_path = Path(__file__).parent.parent / "ui" / "index.html"
fe_path = Path(__file__).parent / "ui" / "index.html"

@app.get("/")
async def serve_frontend_root():
    return FileResponse(fe_path)
