from datetime import datetime, timedelta
from unittest.mock import patch

from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import user_utils
from app.core.config import settings
from app.core.security import verify_password
from app.crud import user_crud
from app.schemas import user_schema
from app.tests.utils.utils import random_email, random_lower_string


async def test_create_user_by_normal_user(
    client: AsyncClient, normal_user_token_headers: dict[str, str], db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = await client.post(
        f"{settings.API_V1_STR}/user/create",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 204
    created_user = await user_crud.get_user_by_email(db=db, email=username)
    assert created_user.email == username
    assert verify_password(password, created_user.password)


async def test_create_user_existing_username(
    client: AsyncClient, normal_user_token_headers: dict[str, str], db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = user_schema.UserCreate(email=username, password=password)
    await user_crud.create_user(db=db, user_create=user_in)
    data = {"email": username, "password": password}
    r = await client.post(
        f"{settings.API_V1_STR}/user/create",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 409


async def test_login_access_token(client: AsyncClient, db: AsyncSession) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = user_schema.UserCreate(email=username, password=password)
    await user_crud.create_user(db=db, user_create=user_in)

    login_data = {
        "username": username,
        "password": password,
    }
    r = await client.post(f"{settings.API_V1_STR}/user/login", data=login_data)

    assert 200 <= r.status_code < 300
    existing_user = await user_crud.get_user_by_email(db=db, email=username)
    assert existing_user


async def test_login_access_token_non_existing_user(
    client: AsyncClient, db: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()

    user = await user_crud.get_user_by_email(db=db, email=username)
    assert user is None

    login_data = {
        "username": username,
        "password": password,
    }
    r = await client.post(f"{settings.API_V1_STR}/user/login", data=login_data)

    assert r.status_code == 401


async def test_request_reset_password(
    client: AsyncClient, db: AsyncSession, normal_user_token_headers: dict[str, str]
) -> None:
    with (
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
    ):
        username = random_email()
        password = random_lower_string()
        user_in = user_schema.UserCreate(email=username, password=password)
        await user_crud.create_user(db=db, user_create=user_in)
        user = await user_crud.get_user_by_email(db=db, email=username)
        assert user is not None

        data = {
            "email": user.email,
        }

        r = await client.post(
            f"{settings.API_V1_STR}/user/password",
            headers=normal_user_token_headers,
            json=data,
        )
        assert r.status_code == 204


async def test_request_reset_password_non_existing_user(
    client: AsyncClient, db: AsyncSession, normal_user_token_headers: dict[str, str]
) -> None:
    username = random_email()
    user = await user_crud.get_user_by_email(db=db, email=username)
    assert user is None

    data = {"email": username}
    r = await client.post(
        f"{settings.API_V1_STR}/user/password",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 404


async def test_reset_password(
    client: AsyncClient, db: AsyncSession, normal_user_token_headers: dict[str, str]
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = user_schema.UserCreate(email=username, password=password)
    await user_crud.create_user(db=db, user_create=user_in)
    user = await user_crud.get_user_by_email(db=db, email=username)
    assert user is not None

    token = user_utils.generate_password_reset_token(email=user.email)
    data = {"new_password": "changethis", "token": token}
    r = await client.post(
        f"{settings.API_V1_STR}/user/reset-password",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 200


async def test_reset_password_invalid_token(
    client: AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {"new_password": "changethis", "token": "invalid"}
    r = await client.post(
        f"{settings.API_V1_STR}/user/reset-password",
        headers=normal_user_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"


async def test_reset_password_expired_token(
    client: AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    username = random_email()
    invalid_hours = -1
    expired_delta = timedelta(hours=invalid_hours)
    now = datetime.utcnow()
    expires = now + expired_delta
    exp = expires.timestamp()
    expired_token = jwt.encode(
        {"exp": exp, "nbf": now, "sub": username},
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    data = {"new_password": "changethis", "token": expired_token}
    r = await client.post(
        f"{settings.API_V1_STR}/user/reset-password",
        headers=normal_user_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"


async def test_reset_password_non_existing_user(
    client: AsyncClient, db: AsyncSession, normal_user_token_headers: dict[str, str]
) -> None:
    username = random_email()
    user = await user_crud.get_user_by_email(db, email=username)
    assert user is None
    non_existing_user_token = user_utils.generate_password_reset_token(email=username)

    data = {"new_password": "changethis", "token": non_existing_user_token}
    r = await client.post(
        f"{settings.API_V1_STR}/user/reset-password",
        headers=normal_user_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 404
    assert (
        response["detail"] == "The user with this email does not exist in the system."
    )
