from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.core.config import settings
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

test_async_engine = create_async_engine(
    str(settings.ASYNC_SQLALCHEMY_DATABASE_URI), echo=False
)
TestAsyncSessionLocal = async_sessionmaker(
    test_async_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def _guard_test_database() -> None:
    if settings.POSTGRES_DB not in ALLOWED_TEST_DB_NAMES:
        raise RuntimeError(
            f"Refusing to run tests: connected to database "
            f"'{settings.POSTGRES_DB}', expected one of {ALLOWED_TEST_DB_NAMES}"
        )


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def db(
    _guard_test_database,
) -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(loop_scope="session")
async def cleanup_api_keys(db: AsyncSession, superuser):
    """Delete all UserAPIKey rows for the superuser before and after each test."""
    keys = await user_api_key_crud.get_user_api_key_list(db, superuser.id)
    for key in keys:
        await user_api_key_crud.delete_api_key(db, key.id)
    yield
    keys = await user_api_key_crud.get_user_api_key_list(db, superuser.id)
    for key in keys:
        await user_api_key_crud.delete_api_key(db, key.id)


@pytest_asyncio.fixture(loop_scope="session")
async def openai_provider(db: AsyncSession):
    """Ensure OpenAI provider exists and return it."""
    provider = await ai_provider_crud.get_provider_by_name(db, "OpenAI")
    if not provider:
        provider = await ai_provider_crud.create_provider(
            db, ai_provider_schema.AIProviderCreate(name="OpenAI")
        )
    return provider


@pytest_asyncio.fixture(loop_scope="session")
async def anthropic_provider(db: AsyncSession):
    """Ensure Anthropic provider exists and return it."""
    provider = await ai_provider_crud.get_provider_by_name(db, "Anthropic")
    if not provider:
        provider = await ai_provider_crud.create_provider(
            db, ai_provider_schema.AIProviderCreate(name="Anthropic")
        )
    return provider


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def normal_user_token_headers(
    client: AsyncClient, db: AsyncSession
) -> dict[str, str]:
    return await authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def test_user(db: AsyncSession) -> User:
    """Fixture to create a test user."""
    email = random_email()
    password = random_lower_string()
    user_in = user_schema.UserCreate(email=email, password=password)
    await user_crud.create_user(db=db, user_create=user_in)
    test_user = await user_crud.get_user_by_email(db=db, email=email)
    return test_user


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def superuser(db: AsyncSession) -> User:
    """Ensure the superuser exists and return it."""
    user = await user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
    if not user:
        user_create = user_schema.UserCreate(
            email=settings.FIRST_SUPERUSER,
            is_superuser=True,
            password=settings.FIRST_SUPERUSER_PASSWORD,
        )
        await user_crud.create_user(db, user_create)
        user = await user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
    return user
