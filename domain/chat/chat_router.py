from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from domain.chat import chat_crud
from domain.chat import chat_schema
from domain.user import user_router, user_schema
router = APIRouter(
    prefix = "/api/chat"
)


@router.get("/titles", response_model=list[dict])
def get_chat_history_titles(db: Session = Depends(get_db), 
                            current_user: user_schema.User = Depends(user_router.get_current_user)):
    db_chat_titles = chat_crud.get_chat_histories(db, current_user.id)
    if not db_chat_titles:
        return []
        # raise HTTPException(status_code=404, detail="No chat found for this user")
    
    chat_titles = [{'id': db_chat_title.id, 'name': db_chat_title.title} for db_chat_title in db_chat_titles]
    return chat_titles

@router.get("/session/{chat_id}")
def get_chat_session_messages(chat_id: int, db: Session = Depends(get_db)):
    db_chat_sessions = chat_crud.get_chat_sessions(db, chat_id)

    res = {"message_history": {
        "messages": []
    }
           }
    if db_chat_sessions:
        res["message_history"]["messages"] = [{"sender": db_chat_session.sender, "text": db_chat_session.message} for db_chat_session in db_chat_sessions]
    return res

@router.post("/session", status_code=status.HTTP_201_CREATED)
def post_chat_session_from_user(_user_chat_sesion_create: chat_schema.UserChatSessionCreate, db: Session = Depends(get_db)):
    chat = chat_crud.get_chat(db, _user_chat_sesion_create.chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="No chat found for this user")
    _chat_session_create = chat_schema.ChatSessionCreate(
        user_id = _user_chat_sesion_create.user_id,
        chat_id = _user_chat_sesion_create.chat_id,
        sender = "user",
        message = _user_chat_sesion_create.message
    )
    chat_session = chat_crud.create_chat_session(
        db=db,
        _chat_session_create=_chat_session_create
    )
    return chat_session