from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, MetaData
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
    social_accounts = relationship("SocialAccount", back_populates = "user")

class SocialAccount(Base):
  __tablename__ = "social_account"
  id = Column(Integer, primary_key = True, index= True)
  user_id = Column(Integer, ForeignKey("user.id"))
  provider = Column(String, nullable = False)
  provider_user_id = Column(String, unique=True, nullable = False)
  user = relationship("User", back_populates = "social_accounts")
