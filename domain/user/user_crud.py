from models import User, SocialAccount
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from domain.user import user_schema

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def create_user(db: Session, user_create: user_schema.UserCreate):
  db_user = User(email = user_create.email,
                 is_social = user_create.is_social,
                 password = pwd_context.hash(user_create.password))
  db.add(db_user)
  db.commit()

def get_existing_user(db: Session, user_create: user_schema.UserCreate):
  return db.query(User).filter(User.email == user_create.email).first()

def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()