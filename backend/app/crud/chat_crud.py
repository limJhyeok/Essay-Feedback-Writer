from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Bot, ChatSession, Conversation
from app.schemas import chat_schema


def get_chat_sessions(db: Session, user_id: int) -> list[ChatSession]:
    chat_sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return chat_sessions


def get_recent_chat_session(db: Session, user_id: int) -> ChatSession | None:
    recent_chat_session = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
        .first()
    )
    return recent_chat_session


def get_conversations(db: Session, chat_session_id: int) -> list[Conversation]:
    conversations = (
        db.query(Conversation)
        .filter(Conversation.chat_session_id == chat_session_id)
        .order_by(Conversation.id.asc())
        .all()
    )
    return conversations


def get_chat_session(db: Session, session_id: int) -> ChatSession:
    chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    return chat_session


def create_conversation(
    db: Session, conversation_create: chat_schema.ConversationCreate
) -> None:
    chat_session = Conversation(
        chat_session_id=conversation_create.chat_session_id,
        sender=conversation_create.sender,
        message=conversation_create.message,
        sender_id=conversation_create.sender_id,
    )
    db.add(chat_session)
    db.commit()


def create_chat_session(
    db: Session, chat_session_create: chat_schema.ChatSessionCreate
) -> ChatSession:
    chat_session = ChatSession(
        user_id=chat_session_create.user_id, title=chat_session_create.title
    )
    db.add(chat_session)
    db.commit()
    return chat_session


def update_chat_session(
    db: Session,
    chat_session: ChatSession,
    chat_session_update_request: chat_schema.ChatSessionUpdateRequest,
) -> None:
    update_dict = chat_session_update_request.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(chat_session, key, value)
    db.add(chat_session)
    db.commit()


def delete_chat_session(db: Session, chat_session_id: int) -> None:
    chat_session = get_chat_session(db, chat_session_id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    db.query(Conversation).filter(
        Conversation.chat_session_id == chat_session_id
    ).delete()

    db.delete(chat_session)
    db.commit()


def get_bot(db: Session, bot_id: int) -> Bot:
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    return bot
