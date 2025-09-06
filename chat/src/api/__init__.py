# src/backend/api/__init__.py

from fastapi import APIRouter
from .chat import router as chat_router
from .tools import router as tools_router

# Create a single API router for all API endpoints
api_router = APIRouter()

# Include individual routers
api_router.include_router(chat_router)
api_router.include_router(tools_router)

# Note: No prefix is used here, as the prefix will be applied in main.py