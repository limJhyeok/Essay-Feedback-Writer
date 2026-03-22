from enum import Enum

from pydantic import BaseModel


class AggregationMethod(str, Enum):
    weighted_average = "weighted_average"
    llm_holistic = "llm_holistic"
    both = "both"


class CriterionSpec(BaseModel):
    name: str
    description: str
    weight: float = 1.0
    scale_min: int = 0
    scale_max: int = 9
    band_descriptors: dict[int, str] = {}
    guidance: str = ""


class RubricSpec(BaseModel):
    name: str
    description: str
    lang: str = "en"
    criteria: list[CriterionSpec]
    overall_scale_min: int = 0
    overall_scale_max: int = 9
    aggregation: AggregationMethod = AggregationMethod.both
    system_prompt_template: str = ""
    human_prompt_template: str = ""
    aggregator_system_prompt: str = ""


class AgentConfig(BaseModel):
    name: str
    description: str = ""
    system_prompt: str
    human_prompt_template: str
    version: str = "1.0"


class CriterionResult(BaseModel):
    name: str = ""
    score: float
    scale_min: int = 0
    scale_max: int = 9
    feedback: str


class ScoringResult(BaseModel):
    overall_score: float
    overall_feedback: str
    scale_min: int = 0
    scale_max: int = 9
    criteria: list[CriterionResult]
