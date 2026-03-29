from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import bot_crud
from app.schemas import bot_schema
from app.tests.utils.utils import random_lower_string


async def test_create_bot_and_get_by_name(db: AsyncSession) -> None:
    name = f"Bot_{random_lower_string()[:8]}"
    bot_create = bot_schema.BotCreate(
        name=name, version="2.0", description="For testing"
    )
    created = await bot_crud.create_bot(db, bot_create)

    assert created.id is not None
    assert created.name == name
    assert created.version == "2.0"

    fetched = await bot_crud.get_bot_by_name(db, name)

    assert fetched is not None
    assert fetched.id == created.id


async def test_get_bots(db: AsyncSession) -> None:
    result = await bot_crud.get_bots(db)

    assert isinstance(result, list)
    assert len(result) >= 1
