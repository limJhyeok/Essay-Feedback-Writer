from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone


class AIProvider(BaseModel):
    id: int
    name: str = Field(..., description="The Provider name of AI model. e.g. OpenAI")
    deprecated: bool = False
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True

    @field_validator("name")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


class AIProviderPublic(BaseModel):
    id: int
    name: str = Field(..., description="The Provider name of AI model. e.g. OpenAI")

    class Config:
        from_attributes = True


class AIProviderCreate(BaseModel):
    name: str = Field(..., description="The Provider name of AI model. e.g. OpenAI")

    @field_validator("name")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v
