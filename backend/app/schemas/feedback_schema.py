from pydantic import BaseModel, Field, field_validator, validator
from datetime import datetime
from typing import Any, Optional


class FeedbackCreate(BaseModel):
    user_id: int
    prompt_id: int
    essay_id: int
    bot_id: int
    content: dict[str, Any] = Field(
        ..., description="The structured JSON content of the feedback"
    )

    created_at: datetime

    @field_validator("content")
    def not_empty(cls, v):
        if not v:
            raise ValueError("null value is not allowed")
        return v


class FeedbackCreateRequest(BaseModel):
    prompt: str
    rubric_name: Optional[str] = None
    essay_content: str = Field(..., description="The text content of the essay")
    api_model_name: str = Field(
        ..., description="The name of the AI model for calling API"
    )

    @field_validator("prompt", "essay_content", "api_model_name")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


class Feedback(BaseModel):
    id: int
    user_id: int
    prompt_id: int
    essay_id: int
    bot_id: int
    content: dict[str, Any] = Field(
        ..., description="The structured JSON content of the feedback"
    )
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackPublic(BaseModel):
    bot_name: str
    content: dict[str, Any] = Field(
        ..., description="The structured JSON content of the feedback"
    )
    created_at: str

    class Config:
        from_attributes = True

    @validator("created_at", pre=True)
    def format_datetime(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M")
        return v
