from unittest.mock import AsyncMock

import pytest

from app.agents.aggregator import Aggregator, _round_half_band
from app.agents.schema import (
    AgentConfig,
    AggregationMethod,
    CriterionResult,
    CriterionSpec,
    RubricSpec,
)


def _make_rubric(aggregation: AggregationMethod = AggregationMethod.both) -> RubricSpec:
    return RubricSpec(
        name="Test",
        description="Test rubric",
        criteria=[
            CriterionSpec(name="C1", description="", weight=1.0),
            CriterionSpec(name="C2", description="", weight=1.0),
            CriterionSpec(name="C3", description="", weight=1.0),
            CriterionSpec(name="C4", description="", weight=1.0),
        ],
        aggregation=aggregation,
    )


def _make_criteria() -> list[CriterionResult]:
    return [
        CriterionResult(name="C1", score=7.0, feedback="Good"),
        CriterionResult(name="C2", score=6.0, feedback="OK"),
        CriterionResult(name="C3", score=7.0, feedback="Good"),
        CriterionResult(name="C4", score=6.0, feedback="OK"),
    ]


def _make_aggregator_agent() -> AgentConfig:
    return AgentConfig(
        name="Aggregator",
        system_prompt="You are an IELTS examiner.",
        human_prompt_template="",
    )


def test_round_half_band():
    assert _round_half_band(6.25) == 6.5
    assert _round_half_band(6.75) == 7.0
    assert _round_half_band(6.0) == 6.0
    assert _round_half_band(6.5) == 6.5
    assert _round_half_band(6.1) == 6.0
    assert _round_half_band(6.9) == 7.0


def test_weighted_average_equal_weights():
    rubric = _make_rubric()
    agg = Aggregator(rubric)
    criteria = _make_criteria()  # 7, 6, 7, 6 → avg 6.5
    assert agg.weighted_average(criteria) == 6.5


def test_weighted_average_unequal_weights():
    rubric = RubricSpec(
        name="Test",
        description="",
        criteria=[
            CriterionSpec(name="C1", description="", weight=2.0),
            CriterionSpec(name="C2", description="", weight=1.0),
        ],
    )
    agg = Aggregator(rubric)
    criteria = [
        CriterionResult(name="C1", score=9.0, feedback=""),
        CriterionResult(name="C2", score=6.0, feedback=""),
    ]
    # (9*2 + 6*1) / 3 = 8.0
    assert agg.weighted_average(criteria) == 8.0


async def test_llm_holistic():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = CriterionResult(
        name="Overall", score=6.5, feedback="Solid essay overall."
    )

    rubric = _make_rubric()
    agg = Aggregator(rubric, mock_llm)
    criteria = _make_criteria()
    agent = _make_aggregator_agent()

    result = await agg.llm_holistic(criteria, agent)
    assert result.score == 6.5
    assert "Solid essay" in result.feedback
    mock_llm.ainvoke.assert_called_once()


async def test_aggregate_both_method():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = CriterionResult(
        name="Overall", score=6.5, feedback="Good overall."
    )

    rubric = _make_rubric(AggregationMethod.both)
    agg = Aggregator(rubric, mock_llm)
    criteria = _make_criteria()
    agent = _make_aggregator_agent()

    result = await agg.aggregate(criteria, agent)
    assert result.overall_score == 6.5
    assert result.overall_feedback == "Good overall."
    assert len(result.criteria) == 4


async def test_aggregate_weighted_average_only():
    rubric = _make_rubric(AggregationMethod.weighted_average)
    agg = Aggregator(rubric)
    criteria = _make_criteria()

    result = await agg.aggregate(criteria)
    assert result.overall_score == 6.5
    assert result.overall_feedback == ""


async def test_aggregate_holistic_requires_agent():
    rubric = _make_rubric(AggregationMethod.llm_holistic)
    agg = Aggregator(rubric, AsyncMock())

    with pytest.raises(ValueError, match="aggregator_agent required"):
        await agg.aggregate(_make_criteria(), aggregator_agent=None)
