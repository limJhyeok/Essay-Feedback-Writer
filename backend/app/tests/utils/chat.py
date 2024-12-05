import os

from sqlalchemy.orm import Session

from app.crud import chat_crud, user_crud
from app.models import ChatSession
from app.schemas import chat_schema
from app.tests.utils.utils import random_lower_string


def create_random_chat_session(db: Session, email: str) -> ChatSession:
    user = user_crud.get_user_by_email(db=db, email=email)
    assert user is not None

    title = random_lower_string()
    item_in = chat_schema.ChatSessionCreate(user_id=user.id, title=title)
    chat_session = chat_crud.create_chat_session(db=db, chat_session_create=item_in)
    return chat_session


def cleanup_file(dir_path: str, file_name: str) -> None:
    file_path = os.path.join(dir_path, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
