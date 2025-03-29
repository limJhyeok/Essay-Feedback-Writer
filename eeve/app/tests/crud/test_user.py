from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.crud import user_crud
from app.schemas import user_schema
from app.tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = user_schema.UserCreate(email=email, password=password)
    user_crud.create_user(db=db, user_create=user_in)
    auth_user = user_crud.authenticate(db=db, email=email, password=password)
    assert auth_user
    assert auth_user.email == email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    auth_user = user_crud.authenticate(db=db, email=email, password=password)
    assert auth_user is None


def test_update_user(db: Session) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = user_schema.UserCreate(email=email, password=password)
    user_crud.create_user(db=db, user_create=user_in)
    created_user = user_crud.get_user_by_email(db=db, email=email)

    new_password = random_lower_string()
    new_password_hashsed = get_password_hash(new_password)
    user_crud.update_user_password(
        db=db, user=created_user, new_password=new_password_hashsed
    )
    updated_user = user_crud.authenticate(db=db, email=email, password=new_password)

    assert updated_user
    assert created_user.email == updated_user.email
