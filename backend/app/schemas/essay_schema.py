from pydantic import BaseModel, Field, field_validator, validator
from datetime import datetime


class EssayCreate(BaseModel):
    user_id: int
    prompt_id: int
    content: str = Field(..., description="The text content of the essay")
    submitted_at: datetime

    @field_validator("content")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


class EssayCreateRequest(BaseModel):
    prompt_id: int
    content: str = Field(..., description="The text content of the essay")

    @field_validator("content")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


class Essay(BaseModel):
    id: int
    user_id: int
    prompt_id: int
    content: str = Field(..., description="The text content of the essay")
    submitted_at: datetime

    class Config:
        from_attributes = True


class EssayPublic(BaseModel):
    id: int
    content: str = Field(..., description="The text content of the essay")
    submitted_at: str

    class Config:
        from_attributes = True

    @validator("submitted_at", pre=True)
    def format_datetime(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M")
        return v
