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
from app.crud import ai_provider_crud
from app.schemas import ai_provider_schema
from app.crud import user_api_key_crud

ALLOWED_TEST_DB_NAMES = ["test"]  # .env variable: TEST_POSTGRES_DB

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def _guard_test_database() -> None:
    """
    Block the test session if not connected to a test database.
    Raise RuntimeError if the connected database is not a known test database.

    Call this before any destructive DB operation in tests to prevent
    accidental data loss in development or production databases.
    """
    if settings.POSTGRES_DB not in ALLOWED_TEST_DB_NAMES:
        raise RuntimeError(
            f"Refusing to run tests: connected to database "
            f"'{settings.POSTGRES_DB}', expected one of {ALLOWED_TEST_DB_NAMES}"
        )


@pytest.fixture(scope="session", autouse=True)
def db(_guard_test_database) -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def cleanup_api_keys(db: Session, superuser):
    """Delete all UserAPIKey rows for the superuser before and after each test."""
    keys = user_api_key_crud.get_user_api_key_list(db, superuser.id)
    for key in keys:
        user_api_key_crud.delete_api_key(db, key.id)
    yield
    keys = user_api_key_crud.get_user_api_key_list(db, superuser.id)
    for key in keys:
        user_api_key_crud.delete_api_key(db, key.id)


@pytest.fixture()
def openai_provider(db: Session):
    """Ensure OpenAI provider exists and return it."""
    provider = ai_provider_crud.get_provider_by_name(db, "OpenAI")
    if not provider:
        provider = ai_provider_crud.create_provider(
            db, ai_provider_schema.AIProviderCreate(name="OpenAI")
        )
    return provider


@pytest.fixture()
def anthropic_provider(db: Session):
    """Ensure Anthropic provider exists and return it."""
    provider = ai_provider_crud.get_provider_by_name(db, "Anthropic")
    if not provider:
        provider = ai_provider_crud.create_provider(
            db, ai_provider_schema.AIProviderCreate(name="Anthropic")
        )
    return provider


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


@pytest.fixture(scope="module")
def superuser(db: Session) -> User:
    """Ensure the superuser exists and return it."""
    user = user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
    if not user:
        user_create = user_schema.UserCreate(
            email=settings.FIRST_SUPERUSER,
            is_superuser=True,
            password=settings.FIRST_SUPERUSER_PASSWORD,
        )
        user_crud.create_user(db, user_create)
        user = user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
    return user
