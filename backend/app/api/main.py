from fastapi import APIRouter

from app.api.routes import chat_router, user_router, util_router

api_router = APIRouter()
api_router.include_router(chat_router.router, prefix="/chat", tags=["chat"])
api_router.include_router(user_router.router, prefix="/user", tags=["user"])
api_router.include_router(util_router.router, prefix="/util", tags=["util"])
