from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from domain.user.user_crud import pwd_context
from domain.user import user_crud, user_schema, user_utils
from starlette import status
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix = "/api/user"
)

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_URL = "/api/user/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)


@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                           db: Session = Depends(get_db)):
    user_email = form_data.username
    user_password = form_data.password
    user = user_crud.get_user(db, user_email)
    if not user or not pwd_context.verify(user_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # make access token
    data = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email
    }

def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"}
    )
    try:
        payload =jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = user_crud.get_user(db, email = user_email)
    if user is None:
        raise credentials_exception
    return user


@router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
  user = user_crud.get_existing_user_for_create(db, user_create = _user_create)
  if user:
    raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail='이미 존재하는 사용자입니다.')
  user_crud.create_user(db = db, user_create = _user_create)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    _user_email: user_schema.UserEmail,
    db: Session = Depends(get_db)
):
    user = user_crud.get_existing_user_for_reset_password(db, user_email=_user_email.email)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email does not exist")

    temp_password = user_utils.generate_temporary_password()
    hashed_password = pwd_context.hash(temp_password)
    user_crud.update_user_password(db, user, hashed_password)
    
    await user_utils.send_temporary_password(user.email, temp_password)