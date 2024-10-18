from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.api.deps import SessionDep
from app.api.utils import user_utils
from app.core import security
from app.core.config import settings
from app.crud import user_crud
from app.schemas import user_schema

router = APIRouter()


@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
) -> dict:
    user_email = form_data.username
    user_password = form_data.password
    user = user_crud.get_user(db, user_email)
    if not user or not security.verify_password(user_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "email": user.email}


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user_schema.UserCreate, db: SessionDep) -> None:
    user = user_crud.get_existing_user_for_create(db, user_create=_user_create)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다."
        )
    user_crud.create_user(db=db, user_create=_user_create)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(_user_email: user_schema.UserEmail, db: SessionDep) -> None:
    user = user_crud.get_existing_user_for_reset_password(
        db, user_email=_user_email.email
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email does not exist"
        )

    temp_password = user_utils.generate_temporary_password()
    hashed_password = security.get_password_hash(temp_password)
    user_crud.update_user_password(db, user, hashed_password)

    await user_utils.send_temporary_password(user.email, temp_password)
