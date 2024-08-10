from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, MetaData, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
Base.metadata = MetaData(naming_convention=naming_convention)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password =  Column(String, nullable=False)
    is_social = Column(Boolean, default = False)
    social_accounts = relationship("SocialAccount", backref = "user")

class SocialAccount(Base):
  __tablename__ = "social_account"
  id = Column(Integer, primary_key = True, index= True)
  user_id = Column(Integer, ForeignKey("user.id"))
  provider = Column(String, nullable = False)
  provider_user_id = Column(String, unique=True, nullable = False)

class Chat(Base):
   __tablename__ = "chat"
   id = Column(Integer, primary_key = True, index= True)
   user_id = Column(Integer, ForeignKey("user.id"))
   title = Column(String, nullable = True)
   created_at = Column(DateTime, default=func.now(), nullable=False)
   updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class ChatSession(Base):
    __tablename__ = "chat_session"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chat.id"), nullable=False)  # 외래 키 추가
    sender = Column(String, nullable=False)
    message = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)