
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, trim_messages
from langchain_core.pydantic_v1 import BaseModel, Field
from sqlalchemy.orm import Session

from app.crud import chat_crud


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: list[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

chat_session_store = {}
retriever_store = {}

def get_chat_session_history_from_dict(chat_session_id: int) -> BaseChatMessageHistory:
    if chat_session_id not in chat_session_store:
        chat_session_store[chat_session_id] = InMemoryChatMessageHistory()
    return chat_session_store[chat_session_id]


def get_chat_session_history_from_db(chat_session_store: dict, db: Session, chat_session_id: int):
    conversations = chat_crud.get_conversations(db, chat_session_id = chat_session_id)
    get_chat_session_history_from_dict(chat_session_id)
    if conversations:
        for conversation in conversations:
            if conversation.sender.value == "user":
                chat_session_store[chat_session_id].add_message(HumanMessage(content = conversation.message))
            elif conversation.sender.value == "bot":
                chat_session_store[chat_session_id].add_message(AIMessage(content=conversation.message))

def get_token_trimmer(model, max_tokens):
    return trim_messages(
    max_tokens=max_tokens,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",  )
