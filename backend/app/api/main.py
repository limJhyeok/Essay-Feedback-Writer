from fastapi import APIRouter

from app.api.routes import user_router, util_router, ielts_router

api_router = APIRouter()
api_router.include_router(user_router.router, prefix="/user", tags=["user"])
api_router.include_router(util_router.router, prefix="/util", tags=["util"])
api_router.include_router(ielts_router.router, prefix="/ielts", tags=["ielts"])
