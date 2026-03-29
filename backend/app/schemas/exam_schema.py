from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class ExamQuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_number: int
    prompt_id: int
    max_points: int
    char_min: Optional[int] = None
    char_max: Optional[int] = None
    passage_refs: Optional[list[str]] = None
    prompt_content: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extract_prompt_content(cls, data):
        if hasattr(data, "prompt") and data.prompt:
            data.__dict__["prompt_content"] = data.prompt.content
        return data


class ExamPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    domain: str
    university: str
    year: int
    track: str
    exam_type: str
    created_at: datetime


class ExamDetailPublic(ExamPublic):
    content: Optional[str] = None
    questions: list[ExamQuestionPublic] = []
