from unittest.mock import AsyncMock

from app.agents.schema import AgentConfig, CriterionResult
from app.agents.swarm import ScoringSwarm


def _make_agent(name: str) -> AgentConfig:
    return AgentConfig(
        name=name,
        system_prompt=f"Evaluate {name}",
        human_prompt_template="Prompt: {essay_prompt}\nEssay: {student_essay}",
    )


async def test_swarm_scores_all_agents():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = CriterionResult(
        name="ignored", score=7.0, feedback="Good"
    )

    swarm = ScoringSwarm(mock_llm, max_concurrency=4)
    swarm.add_agents([_make_agent("C1"), _make_agent("C2"), _make_agent("C3")])

    results = await swarm.score("Write about climate change", "Climate change is...")
    assert len(results) == 3
    assert mock_llm.ainvoke.call_count == 3


async def test_swarm_overwrites_result_name():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = CriterionResult(
        name="wrong_name", score=6.0, feedback="OK"
    )

    swarm = ScoringSwarm(mock_llm)
    swarm.add_agents([_make_agent("Task Response")])

    results = await swarm.score("prompt", "essay")
    assert results[0].name == "Task Response"


async def test_swarm_formats_human_prompt():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = CriterionResult(
        name="", score=5.0, feedback="Average"
    )

    swarm = ScoringSwarm(mock_llm)
    swarm.add_agents([_make_agent("C1")])

    await swarm.score("my prompt", "my essay")

    call_args = mock_llm.ainvoke.call_args[0][0]
    human_msg = call_args[1]
    assert "my prompt" in human_msg.content
    assert "my essay" in human_msg.content


async def test_swarm_passes_system_prompt():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = CriterionResult(
        name="", score=5.0, feedback="Average"
    )

    swarm = ScoringSwarm(mock_llm)
    swarm.add_agents([_make_agent("Task Response")])

    await swarm.score("prompt", "essay")

    call_args = mock_llm.ainvoke.call_args[0][0]
    system_msg = call_args[0]
    assert "Evaluate Task Response" in system_msg.content
