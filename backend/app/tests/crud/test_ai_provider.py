from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import ai_provider_crud
from app.schemas import ai_provider_schema
from app.tests.utils.utils import random_lower_string


async def test_create_provider_and_get_by_name(db: AsyncSession) -> None:
    name = f"Provider_{random_lower_string()[:8]}"
    provider_create = ai_provider_schema.AIProviderCreate(name=name)
    created = await ai_provider_crud.create_provider(db, provider_create)

    assert created.id is not None
    assert created.name == name
    assert created.deprecated is False

    fetched = await ai_provider_crud.get_provider_by_name(db, name)

    assert fetched is not None
    assert fetched.id == created.id


async def test_get_providers(db: AsyncSession) -> None:
    result = await ai_provider_crud.get_providers(db)

    assert isinstance(result, list)
    assert len(result) >= 1
