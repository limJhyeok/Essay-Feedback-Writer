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
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
) -> user_schema.Token:
    user = user_crud.authenticate(
        db=db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    return user_schema.Token(
        access_token=access_token, token_type="bearer", email=user.email
    )


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(user_in: user_schema.UserCreate, db: SessionDep) -> None:
    user = user_crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다."
        )
    user_crud.create_user(db=db, user_create=user_in)


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
async def request_reset_password(
    user_email: user_schema.UserEmail, db: SessionDep
) -> None:
    user = user_crud.get_user_by_email(db, email=user_email.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email does not exist"
        )
    password_reset_token = user_utils.generate_password_reset_token(
        email=user_email.email
    )
    email_data = user_utils.generate_reset_password_email(
        email_to=user.email, email=user_email.email, token=password_reset_token
    )
    user_utils.send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )


@router.post("/reset-password")
def reset_password(db: SessionDep, body: user_schema.NewPassword) -> None:
    """
    Reset password
    """
    email = user_utils.verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = user_crud.get_user_by_email(db=db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    hashed_password = security.get_password_hash(password=body.new_password)
    user_crud.update_user_password(db, user, hashed_password)
