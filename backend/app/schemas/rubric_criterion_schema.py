from pydantic import BaseModel, Field, field_validator


class RubricCriterionCreate(BaseModel):
    rubric_id: int = Field(..., description="The ID of the associated rubric")
    name: str = Field(..., description="The name of the rubric criterion")
    description: str = Field(..., description="Detailed description of the criterion")
    score: int = Field(..., description="Score associated with the criterion")

    @field_validator("name", "description")
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v

    @field_validator("score")
    def not_empty_for_int(cls, v: int) -> int:
        if v is None:
            raise ValueError("null value is not allowed")
        return v


class RubricCriterion(BaseModel):
    id: int
    rubric_id: int
    name: str = Field(..., description="The name of the rubric criterion")
    description: str = Field(..., description="Detailed description of the criterion")
    score: int = Field(..., description="Score associated with the criterion")

    @field_validator("name", "description")
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v

    @field_validator("score")
    def not_empty_for_int(cls, v: int) -> int:
        if v is None:
            raise ValueError("null value is not allowed")
        return v

    class Config:
        from_attributes = True


class RubricCriterionPublic(BaseModel):
    name: str = Field(..., description="The name of the rubric criterion")
    description: str = Field(..., description="Detailed description of the criterion")
    score: int = Field(..., description="Score associated with the criterion")

    @field_validator("name", "description")
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v

    @field_validator("score")
    def not_empty_for_int(cls, v: int) -> int:
        if v is None:
            raise ValueError("null value is not allowed")
        return v

    class Config:
        from_attributes = True
