from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.crud import user_crud
from app.schemas import user_schema
from app.tests.utils.utils import random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/user/login", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = user_crud.get_user_by_email(db=db, email=email)
    if not user:
        user_in_create = user_schema.UserCreate(email=email, password=password)
        user_crud.create_user(db=db, user_create=user_in_create)
        user = user_crud.get_user_by_email(db=db, email=email)
    else:
        if not user.id:
            raise Exception("User id not set")
        hashed_password = security.get_password_hash(password=password)
        user = user_crud.update_user_password(
            db=db, user=user, new_password=hashed_password
        )

    return user_authentication_headers(client=client, email=email, password=password)
