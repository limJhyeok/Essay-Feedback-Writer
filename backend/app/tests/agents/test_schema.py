from app.agents.schema import (
    AgentConfig,
    AggregationMethod,
    CriterionResult,
    CriterionSpec,
    RubricSpec,
    ScoringResult,
)


def test_criterion_spec_defaults():
    spec = CriterionSpec(name="Test", description="A test criterion")
    assert spec.weight == 1.0
    assert spec.scale_min == 0
    assert spec.scale_max == 9
    assert spec.band_descriptors == {}
    assert spec.guidance == ""


def test_criterion_spec_with_band_descriptors():
    spec = CriterionSpec(
        name="Task Response",
        description="How well the essay addresses the prompt",
        band_descriptors={9: "Excellent", 5: "Average", 1: "Poor"},
    )
    assert len(spec.band_descriptors) == 3
    assert spec.band_descriptors[9] == "Excellent"


def test_rubric_spec_defaults():
    rubric = RubricSpec(
        name="Test Rubric",
        description="A test rubric",
        criteria=[CriterionSpec(name="C1", description="Criterion 1")],
    )
    assert rubric.lang == "en"
    assert rubric.aggregation == AggregationMethod.both
    assert rubric.overall_scale_min == 0
    assert rubric.overall_scale_max == 9


def test_aggregation_method_values():
    assert AggregationMethod.weighted_average == "weighted_average"
    assert AggregationMethod.llm_holistic == "llm_holistic"
    assert AggregationMethod.both == "both"


def test_agent_config_creation():
    config = AgentConfig(
        name="Task Response",
        system_prompt="You are an examiner.",
        human_prompt_template="Evaluate: {essay_prompt} {student_essay}",
    )
    assert config.name == "Task Response"
    assert config.version == "1.0"


def test_criterion_result_serialization():
    result = CriterionResult(name="Task Response", score=7.0, feedback="Good work")
    data = result.model_dump()
    assert data["name"] == "Task Response"
    assert data["score"] == 7.0
    assert data["scale_min"] == 0
    assert data["scale_max"] == 9


def test_scoring_result_serialization():
    criteria = [
        CriterionResult(name="C1", score=7.0, feedback="Good"),
        CriterionResult(name="C2", score=6.5, feedback="Decent"),
    ]
    result = ScoringResult(
        overall_score=6.5,
        overall_feedback="Overall decent.",
        criteria=criteria,
    )
    data = result.model_dump()
    assert data["overall_score"] == 6.5
    assert len(data["criteria"]) == 2
