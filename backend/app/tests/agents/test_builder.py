from app.agents.builder import generate_aggregator_agent, generate_criterion_agents
from app.agents.loader import load_rubric


def test_generate_criterion_agents_count():
    rubric = load_rubric(rubric_name="IELTS Writing Task 2")
    agents = generate_criterion_agents(rubric)
    assert len(agents) == 4


def test_generate_criterion_agents_names():
    rubric = load_rubric(rubric_name="IELTS Writing Task 2")
    agents = generate_criterion_agents(rubric)
    names = [a.name for a in agents]
    assert "Task Response" in names
    assert "Coherence & Cohesion" in names
    assert "Lexical Resource" in names
    assert "Grammatical Range & Accuracy" in names


def test_criterion_agent_system_prompt_contains_band_descriptors():
    rubric = load_rubric(rubric_name="IELTS Writing Task 2")
    agents = generate_criterion_agents(rubric)
    for agent in agents:
        # System prompt should contain band score markers
        assert "**9**:" in agent.system_prompt
        assert "**0**:" in agent.system_prompt
        assert agent.name in agent.system_prompt


def test_criterion_agent_human_template_has_placeholders():
    rubric = load_rubric(rubric_name="IELTS Writing Task 2")
    agents = generate_criterion_agents(rubric)
    for agent in agents:
        assert "{essay_prompt}" in agent.human_prompt_template
        assert "{student_essay}" in agent.human_prompt_template


def test_generate_aggregator_agent():
    rubric = load_rubric(rubric_name="IELTS Writing Task 2")
    agent = generate_aggregator_agent(rubric)
    assert agent.name == "Aggregator"
    assert "IELTS examiner" in agent.system_prompt
