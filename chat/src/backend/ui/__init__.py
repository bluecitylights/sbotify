# src/backend/ui/__init__.py

from fastapi import APIRouter
from .chat import router as chat_router
from .tools import router as tools_router

ui_router = APIRouter()

ui_router.include_router(chat_router)
ui_router.include_router(tools_router)
