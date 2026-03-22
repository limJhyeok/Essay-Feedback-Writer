from app.agents.schema import AgentConfig, RubricSpec


def _format_band_descriptors(band_descriptors: dict[int, str]) -> str:
    lines = []
    for score in sorted(band_descriptors.keys(), reverse=True):
        lines.append(f"- **{score}**: {band_descriptors[score]}")
    return "\n".join(lines)


def generate_criterion_agents(rubric: RubricSpec) -> list[AgentConfig]:
    agents = []
    for criterion in rubric.criteria:
        band_text = _format_band_descriptors(criterion.band_descriptors)
        system_prompt = rubric.system_prompt_template.format(
            criteria_name=criterion.name,
            guidance=criterion.guidance,
            band_descriptors=band_text,
        )
        agents.append(
            AgentConfig(
                name=criterion.name,
                description=criterion.description,
                system_prompt=system_prompt,
                human_prompt_template=rubric.human_prompt_template,
            )
        )
    return agents


def generate_aggregator_agent(rubric: RubricSpec) -> AgentConfig:
    return AgentConfig(
        name="Aggregator",
        description="Produces holistic overall score from per-criterion feedbacks",
        system_prompt=rubric.aggregator_system_prompt,
        human_prompt_template="",
    )
