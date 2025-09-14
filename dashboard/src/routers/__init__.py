from fastapi import APIRouter
from .proxy_router import router as proxy_router

ui_router = APIRouter()

ui_router.include_router(proxy_router)
