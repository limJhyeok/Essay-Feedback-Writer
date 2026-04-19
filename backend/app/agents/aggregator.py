from math import floor

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

from app.agents.schema import (
    AggregationMethod,
    AgentConfig,
    CriterionResult,
    RubricSpec,
    ScoringResult,
)


def _round_score(value: float, method: str = "half_band") -> float:
    """Round a score using the specified rounding method."""
    if method == "half_band":
        return floor(value * 2 + 0.5) / 2
    elif method == "integer":
        return round(value)
    elif method == "none":
        return value
    else:
        raise ValueError(f"Unknown rounding method: {method}")


class Aggregator:
    def __init__(self, rubric: RubricSpec, structured_llm: Runnable | None = None):
        self._rubric = rubric
        self._llm = structured_llm

    def weighted_average(self, criteria: list[CriterionResult]) -> float:
        total_weight = sum(spec.weight for spec in self._rubric.criteria)
        weighted_sum = 0.0
        weight_map = {spec.name: spec.weight for spec in self._rubric.criteria}
        for result in criteria:
            w = weight_map.get(result.name, 1.0)
            weighted_sum += result.score * w
        return _round_score(weighted_sum / total_weight, self._rubric.rounding)

    def weighted_sum(self, criteria: list[CriterionResult]) -> float:
        """Sum each criterion's score times its weight, without dividing.

        Suited to rubrics where criteria live on independent point scales
        whose maxima already add up to the overall maximum (e.g. 10+15+20+15=60).
        With weight=1.0 on each criterion the result is the plain sum.
        """
        weight_map = {spec.name: spec.weight for spec in self._rubric.criteria}
        total = 0.0
        for result in criteria:
            total += result.score * weight_map.get(result.name, 1.0)
        return _round_score(total, self._rubric.rounding)

    async def llm_holistic(
        self, criteria: list[CriterionResult], aggregator_agent: AgentConfig
    ) -> CriterionResult:
        if self._llm is None:
            raise RuntimeError("LLM client required for holistic aggregation")

        n_criteria = len(self._rubric.criteria)
        rubric_name = self._rubric.name
        human_prompt = f"Below are scores and feedback for {n_criteria} {rubric_name} scoring criteria.\n"
        for result in criteria:
            human_prompt += f"\n### {result.name}\n{result.feedback}\n"
        human_prompt += "\nNow give the final score and your justification."

        holistic: CriterionResult = await self._llm.ainvoke(
            [
                SystemMessage(content=aggregator_agent.system_prompt),
                HumanMessage(content=human_prompt),
            ]
        )
        return holistic

    async def aggregate(
        self,
        criteria: list[CriterionResult],
        aggregator_agent: AgentConfig | None = None,
    ) -> ScoringResult:
        method = self._rubric.aggregation
        rounding = self._rubric.rounding

        if method == AggregationMethod.weighted_average:
            overall_score = self.weighted_average(criteria)
            overall_feedback = ""
        elif method == AggregationMethod.weighted_sum:
            overall_score = self.weighted_sum(criteria)
            overall_feedback = ""
        elif method == AggregationMethod.llm_holistic:
            if aggregator_agent is None:
                raise ValueError("aggregator_agent required for llm_holistic")
            holistic = await self.llm_holistic(criteria, aggregator_agent)
            overall_score = _round_score(holistic.score, rounding)
            overall_feedback = holistic.feedback
        elif method == AggregationMethod.both:
            if aggregator_agent is None:
                raise ValueError("aggregator_agent required for 'both' aggregation")
            holistic = await self.llm_holistic(criteria, aggregator_agent)
            overall_score = _round_score(holistic.score, rounding)
            overall_feedback = holistic.feedback
        else:
            raise ValueError(f"Unknown aggregation method: {method}")

        return ScoringResult(
            overall_score=overall_score,
            overall_feedback=overall_feedback,
            scale_min=self._rubric.overall_scale_min,
            scale_max=self._rubric.overall_scale_max,
            criteria=criteria,
        )
