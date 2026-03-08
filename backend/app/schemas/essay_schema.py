from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator, validator
from datetime import datetime

from app.models import InputType


class EssayCreate(BaseModel):
    user_id: int
    prompt_id: int
    input_type: InputType = InputType.text
    content: Optional[str] = Field(None, description="The text content of the essay")
    image_path: Optional[str] = None
    ocr_text: Optional[str] = None
    submitted_at: datetime

    @model_validator(mode="after")
    def validate_by_input_type(self):
        if self.input_type == InputType.text:
            if not self.content or not self.content.strip():
                raise ValueError("content is required for text essays")
        elif self.input_type == InputType.handwriting:
            if not self.image_path:
                raise ValueError("image_path is required for handwriting essays")
        return self


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
    input_type: InputType = InputType.text
    content: Optional[str] = Field(None, description="The text content of the essay")
    image_path: Optional[str] = None
    ocr_text: Optional[str] = None
    submitted_at: datetime

    class Config:
        from_attributes = True


class EssayPublic(BaseModel):
    id: int
    input_type: InputType = InputType.text
    content: Optional[str] = Field(None, description="The text content of the essay")
    image_path: Optional[str] = None
    ocr_text: Optional[str] = None
    submitted_at: str

    class Config:
        from_attributes = True

    @validator("submitted_at", pre=True)
    def format_datetime(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M")
        return v
