from sqlalchemy.orm import Session

from app.models import Bot
from app.schemas import bot_schema


def get_bot_by_name(db: Session, name: str) -> Bot:
    bot = db.query(Bot).filter(Bot.name == name).first()
    return bot


def get_bots(db: Session) -> list[bot_schema.Bot]:
    bot = db.query(Bot).all()
    return bot


def create_bot(db: Session, create_bot: bot_schema.BotCreate) -> bot_schema.Bot:
    db_bot = Bot(
        name=create_bot.name,
        version=create_bot.version,
        description=create_bot.description,
        deprecated=False,
    )
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)

    return bot_schema.Bot.from_orm(db_bot)
