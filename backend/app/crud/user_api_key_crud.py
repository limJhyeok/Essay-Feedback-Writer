from datetime import datetime, timezone
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi import HTTPException
from app.models import UserAPIKey
from app.schemas import user_api_key_schema


async def create_user_api_key(
    db: AsyncSession, user_api_key_create: user_api_key_schema.UserAPIKeyCreate
) -> user_api_key_schema.UserAPIKey:
    db_user_api_key = UserAPIKey(
        user_id=user_api_key_create.user_id,
        provider_id=user_api_key_create.provider_id,
        name=user_api_key_create.name,
        api_key=user_api_key_create.api_key,
        registered_at=user_api_key_create.registered_at,
    )
    db.add(db_user_api_key)
    await db.commit()
    await db.refresh(db_user_api_key)

    return user_api_key_schema.UserAPIKey.from_orm(db_user_api_key)


async def get_user_api_key(
    db: AsyncSession, user_id, provider_id
) -> user_api_key_schema.UserAPIKey:
    result = await db.execute(
        select(UserAPIKey).where(
            and_(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider_id == provider_id,
                UserAPIKey.is_active,
            )
        )
    )
    return result.scalars().first()


async def get_user_api_key_list(db: AsyncSession, user_id) -> list[UserAPIKey]:
    result = await db.execute(
        select(UserAPIKey)
        .options(selectinload(UserAPIKey.provider))
        .where(UserAPIKey.user_id == user_id)
    )
    return result.scalars().all()


async def update_last_used(db: AsyncSession, id: int):
    user_api_key = await db.get(UserAPIKey, id)
    if not user_api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    user_api_key.last_used = datetime.now(timezone.utc)
    await db.commit()


async def update_api_key_name(db: AsyncSession, id: int, name: str):
    user_api_key = await db.get(UserAPIKey, id)
    if not user_api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    user_api_key.name = name
    await db.commit()


async def delete_api_key(db: AsyncSession, id: int):
    user_api_key = await db.get(UserAPIKey, id)
    if not user_api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    await db.delete(user_api_key)
    await db.commit()


async def update_to_be_inactive(db: AsyncSession, user_api_key: UserAPIKey):
    user_api_key.is_active = False
    await db.commit()
