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


def _round_half_band(value: float) -> float:
    """Round to nearest 0.5 using round-half-up (IELTS convention)."""
    return floor(value * 2 + 0.5) / 2


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
        return _round_half_band(weighted_sum / total_weight)

    async def llm_holistic(
        self, criteria: list[CriterionResult], aggregator_agent: AgentConfig
    ) -> CriterionResult:
        if self._llm is None:
            raise RuntimeError("LLM client required for holistic aggregation")

        human_prompt = "Below are scores and feedback for four IELTS Writing Task 2 scoring criteria.\n"
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

        if method == AggregationMethod.weighted_average:
            overall_score = self.weighted_average(criteria)
            overall_feedback = ""
        elif method == AggregationMethod.llm_holistic:
            if aggregator_agent is None:
                raise ValueError("aggregator_agent required for llm_holistic")
            holistic = await self.llm_holistic(criteria, aggregator_agent)
            overall_score = _round_half_band(holistic.score)
            overall_feedback = holistic.feedback
        elif method == AggregationMethod.both:
            if aggregator_agent is None:
                raise ValueError("aggregator_agent required for 'both' aggregation")
            holistic = await self.llm_holistic(criteria, aggregator_agent)
            overall_score = _round_half_band(holistic.score)
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
