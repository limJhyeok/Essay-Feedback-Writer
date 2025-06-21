from datetime import datetime, timezone
from sqlalchemy import and_
from sqlalchemy.orm import Session

from fastapi import HTTPException
from app.models import UserAPIKey
from app.schemas import user_api_key_schema


def create_user_api_key(
    db: Session, user_api_key_create: user_api_key_schema.UserAPIKeyCreate
) -> user_api_key_schema.UserAPIKey:
    db_user_api_key = UserAPIKey(
        user_id=user_api_key_create.user_id,
        provider_id=user_api_key_create.provider_id,
        name=user_api_key_create.name,
        api_key=user_api_key_create.api_key,
        registered_at=user_api_key_create.registered_at,
    )
    db.add(db_user_api_key)
    db.commit()
    db.refresh(db_user_api_key)

    return user_api_key_schema.UserAPIKey.from_orm(db_user_api_key)


def get_user_api_key(
    db: Session, user_id, provider_id
) -> user_api_key_schema.UserAPIKey:
    db_api_key = (
        db.query(UserAPIKey)
        .filter(
            and_(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider_id == provider_id,
                UserAPIKey.is_active,
            )
        )
        .first()
    )
    return db_api_key


def get_user_api_key_list(db: Session, user_id) -> list[UserAPIKey]:
    api_key_list = db.query(UserAPIKey).filter(UserAPIKey.user_id == user_id).all()
    return api_key_list


def update_last_used(db: Session, id: int):
    user_api_key = db.get(UserAPIKey, id)
    if not user_api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    user_api_key.last_used = datetime.now(timezone.utc)
    db.commit()


def update_api_key_name(db: Session, id: int, name: str):
    user_api_key = db.get(UserAPIKey, id)
    if not user_api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    user_api_key.name = name
    db.commit()


def update_to_be_inactive(db: Session, user_api_key: UserAPIKey):
    user_api_key.is_active = False
    db.commit()
