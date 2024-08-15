from models import Chat, ChatSession
from sqlalchemy.orm import Session
from domain.chat import chat_schema


def get_chat_histories(db: Session, user_id: int) -> list[Chat]:
    # 쿼리 작성 및 실행
    chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.updated_at.desc()).all()
    return chats

def get_chat_sessions(db: Session, chat_id: int):
    chat_sessions = db.query(ChatSession).filter(ChatSession.chat_id == chat_id).order_by(ChatSession.id.asc()).all()
    return chat_sessions

def get_chat(db: Session, chat_id: int):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    return chat

def create_chat_session(db: Session, _chat_session_create: chat_schema.ChatSessionCreate):
    chat_session = ChatSession(chat_id=_chat_session_create.chat_id, sender=_chat_session_create.sender, message=_chat_session_create.message)
    db.add(chat_session)
    db.commit()