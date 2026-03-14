from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Bot
from app.schemas import bot_schema


async def get_bot_by_name(db: AsyncSession, name: str) -> Bot:
    result = await db.execute(select(Bot).where(Bot.name == name))
    return result.scalars().first()


async def get_bots(db: AsyncSession) -> list[bot_schema.Bot]:
    result = await db.execute(select(Bot))
    return result.scalars().all()


async def create_bot(
    db: AsyncSession, create_bot: bot_schema.BotCreate
) -> bot_schema.Bot:
    db_bot = Bot(
        name=create_bot.name,
        version=create_bot.version,
        description=create_bot.description,
        deprecated=False,
    )
    db.add(db_bot)
    await db.commit()
    await db.refresh(db_bot)

    return bot_schema.Bot.from_orm(db_bot)
