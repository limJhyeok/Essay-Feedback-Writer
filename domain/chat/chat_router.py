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
    chat_histories = chat_crud.get_chat_histories(db, user_id)
    if not chat_histories:
        raise HTTPException(status_code=404, detail="No chat histories found for this user")
    
    chat_history_titles = [{'id': index, 'name': chat.title} for index, chat in enumerate(chat_histories)]
    return chat_history_titles