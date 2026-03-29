from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import api_model_crud, bot_crud
from app.schemas import api_model_schema, bot_schema
from app.tests.utils.utils import random_lower_string


async def test_create_api_model_and_get_by_alias(
    db: AsyncSession, openai_provider
) -> None:
    # create_api_model internally calls get_bot_by_name(db, alias),
    # so a bot with name == alias must exist first
    alias = f"ApiBot_{random_lower_string()[:8]}"
    bot = await bot_crud.create_bot(db, bot_schema.BotCreate(name=alias, version="1.0"))

    model_create = api_model_schema.APIModelCreate(
        api_model_name=f"gpt-4o-{random_lower_string()[:6]}",
        alias=alias,
        provider_name="OpenAI",
    )
    created = await api_model_crud.create_api_model(db, model_create)

    assert created.id is not None
    assert created.api_model_name == model_create.api_model_name
    assert created.alias == alias
    assert created.bot_id == bot.id
    assert created.provider_id == openai_provider.id

    fetched = await api_model_crud.get_api_model_by_alias(db, alias)

    assert fetched is not None
    assert fetched.id == created.id


async def test_get_api_models_by_provider(db: AsyncSession, openai_provider) -> None:
    result = await api_model_crud.get_api_models_by_provider(db, "OpenAI")

    assert isinstance(result, list)
    assert len(result) >= 1
