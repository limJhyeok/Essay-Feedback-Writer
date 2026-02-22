import os
from datetime import datetime, timedelta
from typing import Any
from cryptography.fernet import Fernet

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# TODO: Consider migration passlib to another security library(ref: https://github.com/fastapi/fastapi/discussions/11773)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = os.getenv("ALGORITHM")

# Load secret from env or config file
FERNET_KEY = os.environ["FERNET_SECRET"]
fernet = Fernet(FERNET_KEY)


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def encrypt_api_key(api_key: str) -> str:
    return fernet.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted: str) -> str:
    return fernet.decrypt(encrypted.encode()).decode()
