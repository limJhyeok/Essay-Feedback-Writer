from fastapi import APIRouter

from app.api.routes import chat_router, util_router

api_router = APIRouter()
api_router.include_router(chat_router.router, prefix="/chat", tags=["chat"])
api_router.include_router(util_router.router, prefix="/util", tags=["util"])
