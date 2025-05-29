from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from app import models
from app.schemas import rubric_criterion_schema
from typing import Optional, Dict
import enum


class Rubric(BaseModel):
    id: int
    name: str = Field(..., description="The name of the rubric")
    subject: str = Field(..., description="The subject the rubric is associated with")
    language: models.LanguageType
    description: Optional[str] = None
    scoring_method: models.RubricScoringMethod
    weights: Optional[Dict[str, float]] = None
    created_by: Optional[int] = None
    created_at: datetime
    criteria: list[rubric_criterion_schema.RubricCriterion] = []

    class Config:
        from_attributes = True

    @field_validator("name", "subject")
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v

    @field_validator("language", "scoring_method")
    def not_empty_for_enum(cls, v: enum.Enum) -> enum.Enum:
        if v is None:
            raise ValueError("Enum value cannot be None")
        return v


class RubricCreate(BaseModel):
    name: str = Field(..., description="The name of the rubric")
    subject: str = Field(..., description="The subject the rubric is associated with")
    language: models.LanguageType
    description: Optional[str] = None
    scoring_method: models.RubricScoringMethod
    weights: Optional[Dict[str, float]] = None
    created_by: Optional[int] = None

    @field_validator("name", "subject")
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v

    @field_validator("language", "scoring_method")
    def not_empty_for_enum(cls, v: enum.Enum) -> enum.Enum:
        if v is None:
            raise ValueError("Enum value cannot be None")
        return v
