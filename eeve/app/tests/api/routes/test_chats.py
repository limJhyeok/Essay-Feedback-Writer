import os

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.core.config import settings
from app.definitions import ROOT_DIR
from app.tests.utils.chat import cleanup_file

TEST_DIRECTORY = os.path.join(ROOT_DIR, "tests")
UPLOAD_DIRECTORY = os.path.join(ROOT_DIR, "user-upload")


def test_upload_pdf(client: TestClient, db: Session) -> None:
    email = settings.EMAIL_TEST_USER
    query = text(
        """
        SELECT chat_session.*
        FROM chat_session
        JOIN "user" ON chat_session.user_id = "user".id
        WHERE "user".email = :email;
    """
    )
    result = db.execute(query, {"email": email})
    chat_session = result.fetchone()
    if chat_session is None:
        raise NoResultFound(f"No chat session found for email: {email}")

    chat_session_id = chat_session.id
    test_pdf_name = "dummy.pdf"
    test_pdf_path = os.path.join(TEST_DIRECTORY, test_pdf_name)

    with open(test_pdf_path, "rb") as pdf_file:
        r = client.post(
            f"{settings.API_V1_STR}/chat/{chat_session_id}/upload-pdf/",
            files={"file": (test_pdf_name, pdf_file, "application/pdf")},
        )

    assert r.status_code == 200
    content = r.json()
    assert content["filename"] == test_pdf_name
    assert content["status"] == "processed"

    cleanup_file(UPLOAD_DIRECTORY, test_pdf_name)


# TODO: generate_answer
