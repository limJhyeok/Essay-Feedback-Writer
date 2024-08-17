from pydantic import BaseModel
from typing import Optional

class ChatCreate(BaseModel):
    user_id: int
    title: Optional[str] = "임시 chat"


class ChatCreateRequest(BaseModel):
    title: str


class Chat(BaseModel):
  pass

class ChatSessionCreate(BaseModel):
    chat_id: int
    sender: str
    message: str
    sender_id: int

class UserChatSessionCreateRequest(BaseModel):
    chat_id: int
    sender: str
    message: str
   

class GenerateAnswerRequest(BaseModel):
   chat_id: int
   bot_id: int
   question: str
   context: Optional[list]