from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.db import engine
from app.crud import user_crud
from app.main import app
from app.models import User
from app.schemas import user_schema
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import random_email, random_lower_string

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="module")
def test_user(db: Session) -> User:
    """Fixture to create a test user."""
    email = random_email()
    password = random_lower_string()
    user_in = user_schema.UserCreate(email=email, password=password)
    user_crud.create_user(db=db, user_create=user_in)
    test_user = user_crud.get_user_by_email(db=db, email=email)
    return test_user
