from pydantic import BaseModel
from typing import Optional

class ChatCreate(BaseModel):
    user_id: int
    title: Optional[str] = "임시 chat"

class Chat(BaseModel):
  pass

class ChatSessionCreate(BaseModel):
    user_id: int
    chat_id: int
    sender: str
    message: str

class UserChatSessionCreate(BaseModel):
   chat_id: int
   message: str