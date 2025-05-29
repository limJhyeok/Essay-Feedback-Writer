from pydantic import BaseModel, Field, field_validator, validator
from datetime import datetime, timezone
from typing import Optional


class UserAPIKey(BaseModel):
    id: int
    user_id: int
    provider_id: int
    name: str
    api_key: str = Field(..., description="Hashed api key value")
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime]
    is_active: bool = True

    class Config:
        from_attributes = True

    @field_validator("api_key")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


class UserAPIKeyPublic(BaseModel):
    id: int
    name: str
    provider_name: str
    registered_at: str
    last_used: Optional[str]
    is_active: bool = True

    class Config:
        from_attributes = True

    @validator("registered_at", pre=True)
    def format_registered_at(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M")
        return v

    @validator("last_used", pre=True)
    def format_last_used(cls, v):
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M")
        return v


class UserAPIKeyCreateRequest(BaseModel):
    provider_name: str
    name: str
    api_key: str = Field(..., description="Api key value")
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("api_key")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


def generate_key_name():
    return f"secret-key_{datetime.now(timezone.utc).isoformat()}"


class UserAPIKeyCreate(BaseModel):
    user_id: int
    provider_id: int
    name: str = Field(default_factory=lambda: generate_key_name())
    api_key: str = Field(..., description="Api key value")
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("api_key")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v
