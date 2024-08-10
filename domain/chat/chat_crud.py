from models import Chat, ChatSession
from sqlalchemy.orm import Session
from domain.chat import chat_schema


def get_chat_histories(db: Session, user_id: int) -> list[Chat]:
    # 쿼리 작성 및 실행
    chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.updated_at.desc()).all()
    return chats

def get_chat_session(db: Session, chat_id: int):
    chat_sessions = db.query(ChatSession).filter(ChatSession.chat_id == chat_id).order_by(ChatSession.id.asc()).all()
    return chat_sessions