from pydantic import BaseModel


class GenerateAnswerRequest(BaseModel):
    chat_session_id: int
    bot_id: int
    question: str
    context: list | None
