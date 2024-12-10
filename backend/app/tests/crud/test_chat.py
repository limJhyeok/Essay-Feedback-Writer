from sqlalchemy.orm import Session

from app.crud import chat_crud
from app.models import User
from app.schemas import chat_schema


def test_create_chat_session(db: Session, test_user: User) -> None:
    test_title = "test"
    chat_session_create = chat_schema.ChatSessionCreate(
        user_id=test_user.id, title=test_title
    )

    chat_session = chat_crud.create_chat_session(
        db=db, chat_session_create=chat_session_create
    )
    assert chat_session
    assert chat_session.title == test_title
    assert chat_session.user_id == test_user.id


def test_get_chat_session(db: Session, test_user: User) -> None:
    test_title = "test"
    chat_session_create = chat_schema.ChatSessionCreate(
        user_id=test_user.id, title=test_title
    )

    created_chat_session = chat_crud.create_chat_session(
        db=db, chat_session_create=chat_session_create
    )
    chat_session = chat_crud.get_chat_session(db=db, session_id=created_chat_session.id)
    assert chat_session.id == created_chat_session.id
    assert chat_session.user_id == created_chat_session.user_id
    assert chat_session.title == created_chat_session.title


def test_get_chat_sessions(db: Session, test_user: User) -> None:
    test_title_1 = "test_1"
    chat_session_create_1 = chat_schema.ChatSessionCreate(
        user_id=test_user.id, title=test_title_1
    )
    _ = chat_crud.create_chat_session(db=db, chat_session_create=chat_session_create_1)

    test_title_2 = "test_2"
    chat_session_create_2 = chat_schema.ChatSessionCreate(
        user_id=test_user.id, title=test_title_2
    )
    _ = chat_crud.create_chat_session(db=db, chat_session_create=chat_session_create_2)

    chat_sessions = chat_crud.get_chat_sessions(db=db, user_id=test_user.id)

    assert len(chat_sessions) >= 2


def test_get_recent_chat_session(db: Session, test_user: User) -> None:
    test_title = "test"
    chat_session_create = chat_schema.ChatSessionCreate(
        user_id=test_user.id, title=test_title
    )

    _ = chat_crud.create_chat_session(db=db, chat_session_create=chat_session_create)
    recent_chat_session = chat_crud.get_recent_chat_session(db=db, user_id=test_user.id)

    chat_session_list = chat_crud.get_chat_sessions(db=db, user_id=test_user.id)
    assert chat_session_list[0].id == recent_chat_session.id
    assert chat_session_list[0].user_id == recent_chat_session.user_id
    assert chat_session_list[0].title == recent_chat_session.title


def test_update_chat_session(db: Session, test_user: User) -> None:
    test_title = "test"
    test_update_title = "update_title"
    chat_session_create = chat_schema.ChatSessionCreate(
        user_id=test_user.id, title=test_title
    )

    created_chat_session = chat_crud.create_chat_session(
        db=db, chat_session_create=chat_session_create
    )
    chat_session_update_request = chat_schema.ChatSessionUpdateRequest(
        title=test_update_title
    )
    chat_crud.update_chat_session(
        db=db,
        chat_session=created_chat_session,
        chat_session_update_request=chat_session_update_request,
    )

    updated_chat_session = chat_crud.get_chat_session(
        db=db, session_id=created_chat_session.id
    )
    assert updated_chat_session.id == created_chat_session.id
    assert updated_chat_session.title == test_update_title


def test_delete_chat_session(db: Session, test_user: User) -> None:
    test_title = "test"
    chat_session_create = chat_schema.ChatSessionCreate(
        user_id=test_user.id, title=test_title
    )

    created_chat_session = chat_crud.create_chat_session(
        db=db, chat_session_create=chat_session_create
    )
    chat_crud.delete_chat_session(db=db, chat_session=created_chat_session)

    deleted_chat_session = chat_crud.get_chat_session(
        db=db, session_id=created_chat_session.id
    )

    assert deleted_chat_session is None


def test_create_conversation(db: Session, test_user: User) -> None:
    test_title = "test"
    chat_session_create = chat_schema.ChatSessionCreate(
        user_id=test_user.id, title=test_title
    )

    created_chat_session = chat_crud.create_chat_session(
        db=db, chat_session_create=chat_session_create
    )

    test_message = "test_message"
    conversation_create = chat_schema.ConversationCreate(
        chat_session_id=created_chat_session.id,
        sender="user",
        message=test_message,
        sender_id=test_user.id,
    )

    created_conversation = chat_crud.create_conversation(
        db=db, conversation_create=conversation_create
    )
    assert created_conversation.chat_session_id == created_chat_session.id
    assert created_conversation.sender_id == test_user.id
    assert created_conversation.message == test_message


def test_get_conversations(db: Session, test_user: User) -> None:
    test_title = "test"
    chat_session_create = chat_schema.ChatSessionCreate(
        user_id=test_user.id, title=test_title
    )

    created_chat_session = chat_crud.create_chat_session(
        db=db, chat_session_create=chat_session_create
    )

    test_sender_1 = "user"
    test_message_1 = "test_message_1"

    test_sender_2 = "user"
    test_message_2 = "teste_message_2"

    conversation_create_1 = chat_schema.ConversationCreate(
        chat_session_id=created_chat_session.id,
        sender=test_sender_1,
        message=test_message_1,
        sender_id=test_user.id,
    )
    conversation_create_2 = chat_schema.ConversationCreate(
        chat_session_id=created_chat_session.id,
        sender=test_sender_2,
        message=test_message_2,
        sender_id=test_user.id,
    )

    _ = chat_crud.create_conversation(db=db, conversation_create=conversation_create_1)
    _ = chat_crud.create_conversation(db=db, conversation_create=conversation_create_2)

    conversations = chat_crud.get_conversations(
        db=db, chat_session_id=created_chat_session.id
    )

    assert len(conversations) >= 2
