import os

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import chat_crud, user_crud
from app.definitions import ROOT_DIR
from app.schemas import chat_schema
from app.tests.utils.chat import cleanup_file, create_random_chat_session

TEST_DIRECTORY = os.path.join(ROOT_DIR, "tests")
UPLOAD_DIRECTORY = os.path.join(ROOT_DIR, "user-upload")


def test_get_chat_history_titles(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    email = settings.EMAIL_TEST_USER
    create_random_chat_session(db=db, email=email)
    create_random_chat_session(db=db, email=email)

    r = client.get(
        f"{settings.API_V1_STR}/chat/titles",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 200
    content = r.json()
    assert len(content["data"]) >= 2


def test_get_recent_chat_session_id(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    email = settings.EMAIL_TEST_USER
    created_chat_session = create_random_chat_session(db=db, email=email)

    r = client.get(
        f"{settings.API_V1_STR}/chat/recent",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 200
    content = r.json()
    assert content["id"] == created_chat_session.id


def test_get_chat_session_message_list_of_empty(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    email = settings.EMAIL_TEST_USER
    created_chat_session = create_random_chat_session(db=db, email=email)

    r = client.get(
        f"{settings.API_V1_STR}/chat/session/{created_chat_session.id}",
        headers=normal_user_token_headers,
    )
    content = r.json()
    assert len(content["data"]) == 0


def test_get_chat_session_message_list_of_non_empty(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    email = settings.EMAIL_TEST_USER
    created_chat_session = create_random_chat_session(db=db, email=email)

    user = user_crud.get_user_by_email(db=db, email=email)

    test_sender = "user"
    test_message = "test"

    conversation_create = chat_schema.ConversationCreate(
        chat_session_id=created_chat_session.id,
        sender=test_sender,
        message=test_message,
        sender_id=user.id,
    )
    chat_crud.create_conversation(db=db, conversation_create=conversation_create)
    r = client.get(
        f"{settings.API_V1_STR}/chat/session/{created_chat_session.id}",
        headers=normal_user_token_headers,
    )
    content = r.json()
    assert len(content["data"]) == 1

    conversation = content["data"][0]
    assert conversation["sender"] == test_sender
    assert conversation["text"] == test_message


def test_create_chat(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {"title": "test title"}
    r = client.post(
        f"{settings.API_V1_STR}/chat/create",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 201


def test_rename_chat_session(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    email = settings.EMAIL_TEST_USER
    created_chat_session = create_random_chat_session(db=db, email=email)

    data = {"title": "test title"}

    r = client.put(
        f"{settings.API_V1_STR}/chat/rename/{created_chat_session.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300


def test_rename_non_existing_chat_session(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    non_exist_chat_session_id = -1
    data = {"title": "test title"}

    r = client.put(
        f"{settings.API_V1_STR}/chat/rename/{non_exist_chat_session_id}",
        headers=normal_user_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 404
    assert response["detail"] == "chat session not found"


def test_delete_chat(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    email = settings.EMAIL_TEST_USER
    created_chat_session = create_random_chat_session(db=db, email=email)
    r = client.delete(
        f"{settings.API_V1_STR}/chat/delete/{created_chat_session.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 200


def test_delete_non_existing_chat(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    non_exist_chat_session_id = -1
    r = client.delete(
        f"{settings.API_V1_STR}/chat/delete/{non_exist_chat_session_id}",
        headers=normal_user_token_headers,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 404
    assert response["detail"] == "chat session not found"


def test_post_user_conversation_of_non_existing_chat(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    non_exist_chat_session_id = -1
    data = {
        "chat_session_id": non_exist_chat_session_id,
        "sender": "user",
        "message": "test",
    }
    r = client.post(
        f"{settings.API_V1_STR}/chat/session",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 201


def test_post_user_conversation(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    email = settings.EMAIL_TEST_USER
    created_chat_session = create_random_chat_session(db=db, email=email)
    data = {
        "chat_session_id": created_chat_session.id,
        "sender": "user",
        "message": "test",
    }
    r = client.post(
        f"{settings.API_V1_STR}/chat/session",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 201


def test_upload_pdf(client: TestClient, db: Session) -> None:
    email = settings.EMAIL_TEST_USER
    created_chat_session = create_random_chat_session(db=db, email=email)
    chat_session_id = created_chat_session.id

    test_pdf_name = "dummy.pdf"
    test_pdf_path = os.path.join(TEST_DIRECTORY, test_pdf_name)

    with open(test_pdf_path, "rb") as pdf_file:
        response = client.post(
            f"{settings.API_V1_STR}/chat/{chat_session_id}/upload-pdf/",
            files={"file": (test_pdf_name, pdf_file, "application/pdf")},
        )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["filename"] == test_pdf_name
    assert json_response["status"] == "processed"

    cleanup_file(UPLOAD_DIRECTORY, test_pdf_name)


# TODO: generate_answer
