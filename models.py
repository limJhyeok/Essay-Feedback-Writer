from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# TODO: add another attributes
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
