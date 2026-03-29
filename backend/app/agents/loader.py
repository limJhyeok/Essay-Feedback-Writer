from functools import lru_cache
from pathlib import Path

import yaml

from app.agents.schema import AggregationMethod, CriterionSpec, RubricSpec

_CONFIGS_DIR = Path(__file__).parent / "configs"

_RUBRIC_REGISTRY: dict[str, str] = {
    "IELTS Writing Task 2": "ielts_task2.yaml",
    "KSAT 2025 CAU Humanities Q1": "ksat/cau_2025_humanities_q1.yaml",
    "KSAT 2025 CAU Humanities Q2": "ksat/cau_2025_humanities_q2.yaml",
    "KSAT 2025 CAU Humanities Q3": "ksat/cau_2025_humanities_q3.yaml",
}


@lru_cache(maxsize=16)
def load_rubric(
    yaml_path: str | None = None, rubric_name: str | None = None
) -> RubricSpec:
    if yaml_path is None and rubric_name is not None:
        filename = _RUBRIC_REGISTRY.get(rubric_name)
        if filename is None:
            raise ValueError(f"Unknown rubric: {rubric_name}")
        yaml_path = str(_CONFIGS_DIR / filename)
    elif yaml_path is None:
        raise ValueError("Either yaml_path or rubric_name must be provided")

    with open(yaml_path) as f:
        raw = yaml.safe_load(f)

    criteria = []
    for c in raw["criteria"]:
        criteria.append(
            CriterionSpec(
                name=c["name"],
                description=c.get("description", ""),
                weight=c.get("weight", 1.0),
                scale_min=c.get("scale_min", 0),
                scale_max=c.get("scale_max", 9),
                band_descriptors={
                    int(k): v for k, v in c.get("band_descriptors", {}).items()
                },
                guidance=c.get("guidance", ""),
            )
        )

    return RubricSpec(
        name=raw["name"],
        description=raw.get("description", ""),
        lang=raw.get("lang", "en"),
        criteria=criteria,
        overall_scale_min=raw.get("overall_scale_min", 0),
        overall_scale_max=raw.get("overall_scale_max", 9),
        aggregation=AggregationMethod(raw.get("aggregation", "both")),
        rounding=raw.get("rounding", "half_band"),
        system_prompt_template=raw.get("system_prompt_template", ""),
        human_prompt_template=raw.get("human_prompt_template", ""),
        aggregator_system_prompt=raw.get("aggregator_system_prompt", ""),
    )
