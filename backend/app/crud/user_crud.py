from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas import user_schema


def create_user(db: Session, user_create: user_schema.UserCreate) -> None:
    db_user = User(
        email=user_create.email,
        is_social=user_create.is_social,
        password=get_password_hash(user_create.password),
    )
    db.add(db_user)
    db.commit()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def update_user_password(db: Session, user: User, new_password: str) -> None:
    user.password = new_password
    db.commit()


def get_existing_user_for_reset_password(
    db: Session, user_email: EmailStr
) -> User | None:
    return db.query(User).filter(User.email == user_email).first()


def authenticate(db: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(db=db, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.password):
        return None
    return db_user
