from models import Chat
from sqlalchemy.orm import Session
from domain.chat import chat_schema


def get_chat_histories(db: Session, user_id: int) -> list[Chat]:
    # 쿼리 작성 및 실행
    chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.updated_at.desc()).all()
    return chats