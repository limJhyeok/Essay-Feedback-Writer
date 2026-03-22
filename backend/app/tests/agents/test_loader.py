import pytest

from app.agents.loader import load_rubric
from app.agents.schema import AggregationMethod


def test_load_ielts_task2_by_name():
    rubric = load_rubric(rubric_name="IELTS Writing Task 2")
    assert rubric.name == "IELTS Writing Task 2"
    assert rubric.lang == "en"
    assert rubric.aggregation == AggregationMethod.both
    assert len(rubric.criteria) == 4


def test_load_ielts_task2_criteria_names():
    rubric = load_rubric(rubric_name="IELTS Writing Task 2")
    names = [c.name for c in rubric.criteria]
    assert "Task Response" in names
    assert "Coherence & Cohesion" in names
    assert "Lexical Resource" in names
    assert "Grammatical Range & Accuracy" in names


def test_load_ielts_task2_band_descriptors():
    rubric = load_rubric(rubric_name="IELTS Writing Task 2")
    for criterion in rubric.criteria:
        # Should have bands 0-9
        assert len(criterion.band_descriptors) == 10
        assert 9 in criterion.band_descriptors
        assert 0 in criterion.band_descriptors


def test_load_ielts_task2_has_prompts():
    rubric = load_rubric(rubric_name="IELTS Writing Task 2")
    assert "{criteria_name}" in rubric.system_prompt_template
    assert "{essay_prompt}" in rubric.human_prompt_template
    assert "{student_essay}" in rubric.human_prompt_template
    assert rubric.aggregator_system_prompt != ""


def test_load_ielts_task2_criteria_have_guidance():
    rubric = load_rubric(rubric_name="IELTS Writing Task 2")
    for criterion in rubric.criteria:
        assert criterion.guidance != "", f"{criterion.name} missing guidance"


def test_load_rubric_unknown_name_raises():
    with pytest.raises(ValueError, match="Unknown rubric"):
        load_rubric(rubric_name="Nonexistent Rubric")


def test_load_rubric_no_args_raises():
    with pytest.raises(ValueError, match="Either yaml_path or rubric_name"):
        load_rubric()
