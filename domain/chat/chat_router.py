from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from domain.chat import chat_crud
router = APIRouter(
    prefix = "/api/chat"
)


@router.get("/titles/{user_id}")
def get_chat_history_titles(user_id: int, db: Session = Depends(get_db)):
    db_chat_titles = chat_crud.get_chat_histories(db, user_id)
    if not db_chat_titles:
        raise HTTPException(status_code=404, detail="No chat found for this user")
    
    chat_titles = [{'id': db_chat_title.id, 'name': db_chat_title.title} for db_chat_title in db_chat_titles]
    return chat_titles

@router.get("/session/{chat_id}")
def get_chat_session_messages(chat_id: int, db: Session = Depends(get_db)):
    db_chat_sessions = chat_crud.get_chat_session(db, chat_id)

    res = {"message_history": {
        "messages": []
    }
           }
    if db_chat_sessions:
        res["message_history"]["messages"] = [{"sender": db_chat_session.sender, "text": db_chat_session.message} for db_chat_session in db_chat_sessions]
    return res
