from sqlalchemy.orm import Session

from app.models import AIProvider
from app.schemas import ai_provider_schema


def get_provider_by_name(
    db: Session, provider_name: str
) -> ai_provider_schema.AIProvider:
    api_model = db.query(AIProvider).filter(AIProvider.name == provider_name).first()
    return api_model


def create_provider(
    db: Session, provider_create: ai_provider_schema.AIProviderCreate
) -> ai_provider_schema.AIProvider:
    new_ai_provider = AIProvider(name=provider_create.name)
    db.add(new_ai_provider)
    db.commit()
    db.refresh(new_ai_provider)

    return ai_provider_schema.AIProvider.from_orm(new_ai_provider)


def get_providers(db: Session) -> list[ai_provider_schema.AIProvider]:
    providers = db.query(AIProvider).all()
    return providers
