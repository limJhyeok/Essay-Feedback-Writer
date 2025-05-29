from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class ExampleEssayCreate(BaseModel):
    prompt_id: int
    content: str = Field(..., description="The text content of the essay")
    created_at: datetime
    updated_at: datetime

    @field_validator("content")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


class ExampleEssay(BaseModel):
    id: int
    prompt_id: int
    content: str = Field(..., description="The text content of the essay")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
