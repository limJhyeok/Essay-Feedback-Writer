from datetime import datetime, timezone

from fastapi import APIRouter
from starlette import status

from app.api.deps import CurrentUser, SessionDep
from app.core import security
from app.crud import (
    ai_provider_crud,
    api_model_crud,
    bot_crud,
    user_api_key_crud,
)
from app.schemas import (
    ai_provider_schema,
    api_model_schema,
    bot_schema,
    user_api_key_schema,
)

router = APIRouter()


@router.get("/bots", response_model=list[bot_schema.BotPublic])
async def read_bots(db: SessionDep) -> list[bot_schema.BotPublic]:
    return await bot_crud.get_bots(db)


@router.get("/providers", response_model=list[ai_provider_schema.AIProviderPublic])
async def read_providers(db: SessionDep) -> list[ai_provider_schema.AIProviderPublic]:
    return await ai_provider_crud.get_providers(db)


@router.get(
    "/api_models/{provider_name}", response_model=list[api_model_schema.APIModelPublic]
)
async def read_api_models(
    db: SessionDep, provider_name: str
) -> list[api_model_schema.APIModelPublic]:
    return await api_model_crud.get_api_models_by_provider(db, provider_name)


def _generate_key_name():
    return f"secret-key_{datetime.now(timezone.utc).isoformat()}"


@router.post("/api_keys", status_code=status.HTTP_204_NO_CONTENT)
async def create_api_key(
    db: SessionDep,
    current_user: CurrentUser,
    request: user_api_key_schema.UserAPIKeyCreateRequest,
):
    provider = await ai_provider_crud.get_provider_by_name(db, request.provider_name)
    user_api_key_create = user_api_key_schema.UserAPIKeyCreate(
        user_id=current_user.id,
        provider_id=provider.id,
        name=request.name or _generate_key_name(),
        api_key=security.encrypt_api_key(request.api_key),
    )
    _ = await user_api_key_crud.create_user_api_key(db, user_api_key_create)


@router.get("/api_keys", response_model=list[user_api_key_schema.UserAPIKeyPublic])
async def get_api_key_list(
    db: SessionDep, current_user: CurrentUser
) -> list[user_api_key_schema.UserAPIKeyPublic]:
    user_api_key_list = await user_api_key_crud.get_user_api_key_list(
        db, current_user.id
    )
    response = []
    for user_api_key in user_api_key_list:
        item = user_api_key_schema.UserAPIKeyPublic(
            id=user_api_key.id,
            name=user_api_key.name,
            provider_name=user_api_key.provider.name,
            registered_at=user_api_key.registered_at,
            last_used=user_api_key.last_used,
            is_active=user_api_key.is_active,
        )
        response.append(item)

    return response


@router.put("/api_keys/{api_key_id}/name", status_code=status.HTTP_204_NO_CONTENT)
async def rename_api_key(
    db: SessionDep,
    api_key_id: int,
    request: user_api_key_schema.UserAPIKeyRenameRequest,
) -> None:
    await user_api_key_crud.update_api_key_name(db, api_key_id, request.name)


@router.delete("/api_keys/{api_key_id}")
async def delete_api_key_route(db: SessionDep, api_key_id: int) -> None:
    await user_api_key_crud.delete_api_key(db, api_key_id)
