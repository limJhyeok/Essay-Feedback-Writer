from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone


class APIModel(BaseModel):
    id: int
    bot_id: int
    provider_id: int

    api_model_name: str = Field(
        ...,
        description="The model name for calling the API from the provider. e.g. gpt-4o",
    )
    alias: str = Field(..., description="The alias for user-friednly name. e.g. GPT-4o")
    deprecated: bool = False
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True

    @field_validator("api_model_name")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v


class APIModelPublic(BaseModel):
    id: int
    api_model_name: str = Field(
        ...,
        description="The model name for calling the API from the provider. e.g. gpt-4o",
    )
    alias: str = Field(..., description="The alias for user-friednly name. e.g. GPT-4o")
    deprecated: bool = False

    class Config:
        from_attributes = True


class APIModelCreate(BaseModel):
    api_model_name: str = Field(
        ...,
        description="The model name for calling the API from the provider. e.g. gpt-4o",
    )
    alias: str = Field(..., description="The alias for user-friednly name. e.g. GPT-4o")
    provider_name: str = Field(..., description="The provider name of an AI model")

    @field_validator("api_model_name")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v
