from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class PromptCreate(BaseModel):
    content: str = Field(..., description="The text content of the prompt")
    created_by: int
    created_at: datetime
    updated_at: datetime

    @field_validator("content")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


class PromptReaction(BaseModel):
    id: int
    reaction: str


class Prompt(BaseModel):
    id: int
    content: str = Field(..., description="The text content of the prompt")
    created_by: int
    created_at: datetime
    updated_at: datetime
    reactions: list[PromptReaction] = []

    class Config:
        from_attributes = True


class PromptList(BaseModel):
    data: list[Prompt]
