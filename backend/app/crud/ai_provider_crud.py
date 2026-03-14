from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIProvider
from app.schemas import ai_provider_schema


async def get_provider_by_name(
    db: AsyncSession, provider_name: str
) -> ai_provider_schema.AIProvider:
    result = await db.execute(
        select(AIProvider).where(AIProvider.name == provider_name)
    )
    return result.scalars().first()


async def create_provider(
    db: AsyncSession, provider_create: ai_provider_schema.AIProviderCreate
) -> ai_provider_schema.AIProvider:
    new_ai_provider = AIProvider(name=provider_create.name)
    db.add(new_ai_provider)
    await db.commit()
    await db.refresh(new_ai_provider)

    return ai_provider_schema.AIProvider.from_orm(new_ai_provider)


async def get_providers(db: AsyncSession) -> list[ai_provider_schema.AIProvider]:
    result = await db.execute(select(AIProvider))
    return result.scalars().all()
