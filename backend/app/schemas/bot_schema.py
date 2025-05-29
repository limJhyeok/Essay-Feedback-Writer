from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional


class Bot(BaseModel):
    id: int
    name: str
    version: Optional[str] = None
    description: Optional[str] = Field(
        None, description="The description of the AI model"
    )
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator("name")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


class BotPublic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

    @field_validator("name")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


class BotCreate(BaseModel):
    name: str
    version: Optional[str] = None
    description: Optional[str] = Field(
        None, description="The description of the AI model"
    )

    class Config:
        from_attributes = True

    @field_validator("name")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v
