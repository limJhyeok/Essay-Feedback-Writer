from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud import ai_provider_crud, bot_crud
from app.models import APIModel, AIProvider
from app.schemas import api_model_schema


def get_api_model_by_alias(db: Session, alias: str) -> api_model_schema.APIModel:
    api_model = db.query(APIModel).filter(APIModel.alias == alias).first()
    return api_model


def get_api_models_by_provider(
    db: Session, provider_name: str
) -> list[api_model_schema.APIModel]:
    api_models = (
        db.query(APIModel)
        .join(AIProvider)
        .filter(AIProvider.name == provider_name)
        .all()
    )

    return api_models


def get_api_model_by_name_and_provider(
    db: Session, api_model_name: str, provider_name: str
) -> api_model_schema.APIModel | None:
    return (
        db.query(APIModel)
        .join(AIProvider)
        .filter(
            and_(
                AIProvider.name == provider_name,
                APIModel.api_model_name == api_model_name,
            )
        )
        .first()
    )


def create_api_model(
    db: Session, api_model_create: api_model_schema.APIModelCreate
) -> api_model_schema.APIModel:
    new_api_model = APIModel(
        bot_id=bot_crud.get_bot_by_name(db, api_model_create.alias).id,
        provider_id=ai_provider_crud.get_provider_by_name(
            db, api_model_create.provider_name
        ).id,
        api_model_name=api_model_create.api_model_name,
        alias=api_model_create.alias,
    )

    db.add(new_api_model)
    db.commit()
    db.refresh(new_api_model)

    return api_model_schema.APIModel.from_orm(new_api_model)
