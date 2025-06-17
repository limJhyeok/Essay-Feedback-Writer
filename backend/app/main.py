from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.ENVIRONMENT == "production":
    docs_url = None
    redoc_url = None
    openapi_url = None
else:
    docs_url = "/docs"
    redoc_url = "/redoc"
    openapi_url = f"{settings.API_V1_STR}/openapi.json"

app = FastAPI(
    title=settings.PROJECT_NAME,
    generate_unique_id_function=custom_generate_unique_id,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)

if settings.ENVIRONMENT == "production":
    setattr(app, "docs_url", None)
    setattr(app, "redoc_url", None)
    setattr(app, "openapi_url", None)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
