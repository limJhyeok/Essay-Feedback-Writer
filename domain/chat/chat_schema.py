from pydantic import BaseModel
from datetime import datetime

class ChatCreate(BaseModel):
    pass

class Chat(BaseModel):
  pass

class ChatSessionCreate(BaseModel):
    user_id: int
    chat_id: int
    sender: str
    message: str

class UserChatSessionCreate(BaseModel):
   user_id: int
   chat_id: int
   message: str