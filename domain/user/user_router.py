from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from domain.user.user_crud import pwd_context
from domain.user import user_crud, user_schema, user_utils
from starlette import status
from jose import jwt
from dotenv import load_dotenv
import os
from pydantic import EmailStr

router = APIRouter(
    prefix = "/api/user"
)

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("ALGORITHM")
ALGORITHM = os.getenv("ALGORITHM")

class OAuth2EmailPasswordRequestForm:
    def __init__(self, email: str = Form(...), password: str = Form(...)):
        self.email = email
        self.password = password

@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(form_data: OAuth2EmailPasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    # check user and password
    user = user_crud.get_user(db, form_data.email)
    if not user or not pwd_context.verify(form_data.password, user.password):
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

@router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
  user = user_crud.get_existing_user_for_create(db, user_create = _user_create)
  if user:
    raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail='이미 존재하는 사용자입니다.')
  user_crud.create_user(db = db, user_create = _user_create)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    user_email: EmailStr, 
    db: Session = Depends(get_db)
):
    user = user_crud.get_existing_user_for_reset_password(db, user_email=user_email)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email does not exist")

    # 임시 비밀번호 생성 및 업데이트
    temp_password = user_utils.generate_temporary_password()
    hashed_password = pwd_context.hash(temp_password)
    user_crud.update_user_password(db, user, hashed_password)
    
    # 임시 비밀번호 이메일로 발송
    await user_utils.send_temporary_password(user.email, temp_password)