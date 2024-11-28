from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password
from app.crud import user_crud
from app.schemas import user_schema
from app.tests.utils.utils import random_email, random_lower_string


def test_create_user_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/user/create",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 204
    created_user = user_crud.get_user_by_email(db=db, email=username)
    assert created_user.email == username
    assert verify_password(password, created_user.password)


def test_create_user_existing_username(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = user_schema.UserCreate(email=username, password=password)
    user_crud.create_user(db=db, user_create=user_in)
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/user/create",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 409


def test_login_access_token(client: TestClient, db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = user_schema.UserCreate(email=username, password=password)
    user_crud.create_user(db=db, user_create=user_in)

    login_data = {
        "username": username,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/user/login", data=login_data)

    assert 200 <= r.status_code < 300
    existing_user = user_crud.get_user_by_email(db=db, email=username)
    assert existing_user


def test_login_access_token_non_existing_user(client: TestClient, db: Session) -> None:
    username = random_email()
    password = random_lower_string()

    user = user_crud.get_user_by_email(db=db, email=username)
    assert user is None

    login_data = {
        "username": username,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/user/login", data=login_data)

    assert r.status_code == 401
