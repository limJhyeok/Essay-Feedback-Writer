import asyncio

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

from app.agents.schema import AgentConfig, CriterionResult


class ScoringSwarm:
    def __init__(self, structured_llm: Runnable, max_concurrency: int = 4):
        self._llm = structured_llm
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._agents: list[AgentConfig] = []

    def add_agents(self, agents: list[AgentConfig]) -> None:
        self._agents.extend(agents)

    async def _score_one(
        self, agent: AgentConfig, essay_prompt: str, student_essay: str
    ) -> CriterionResult:
        async with self._semaphore:
            human_prompt = agent.human_prompt_template.format(
                essay_prompt=essay_prompt, student_essay=student_essay
            )
            result: CriterionResult = await self._llm.ainvoke(
                [
                    SystemMessage(content=agent.system_prompt),
                    HumanMessage(content=human_prompt),
                ]
            )
            # Overwrite name to avoid relying on LLM output
            result.name = agent.name
            return result

    async def score(
        self, essay_prompt: str, student_essay: str
    ) -> list[CriterionResult]:
        tasks = [
            self._score_one(agent, essay_prompt, student_essay)
            for agent in self._agents
        ]
        return list(await asyncio.gather(*tasks))
