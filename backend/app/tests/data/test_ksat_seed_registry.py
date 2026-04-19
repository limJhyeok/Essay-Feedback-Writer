"""Structural tests for the KSAT seed registry.

These tests verify the shape of each registered exam — that seed.py
modules expose the expected attributes, that referenced markdown files
exist and are non-empty, and that domain-specific expectations hold
(e.g. CAU's three questions share identical passage content, Inha Q2
references the expected graph image paths).

They do not touch the database; integration with store_ksat_exam_data
is covered by the API route tests that seed live fixtures.
"""

import re

from app.data.ksat.seed_ksat_data import SEED_EXAMS


REQUIRED_META_KEYS = {"university", "year", "track", "exam_type"}
REQUIRED_QUESTION_KEYS = {
    "question_number",
    "passage_path",
    "prompt_path",
    "max_points",
}


def test_registry_not_empty():
    assert len(SEED_EXAMS) >= 1


def test_every_exam_has_well_formed_meta():
    for exam in SEED_EXAMS:
        assert hasattr(exam, "EXAM_META"), f"{exam.__name__} missing EXAM_META"
        assert REQUIRED_META_KEYS.issubset(
            exam.EXAM_META.keys()
        ), f"{exam.__name__} EXAM_META missing keys"
        assert exam.EXAM_META["track"] in {"humanities", "sciences"}
        assert exam.EXAM_META["exam_type"] in {"mock", "official"}


def test_every_question_references_readable_files():
    for exam in SEED_EXAMS:
        for q in exam.QUESTIONS:
            missing = REQUIRED_QUESTION_KEYS - q.keys()
            assert (
                not missing
            ), f"{exam.__name__} Q{q.get('question_number')} missing {missing}"
            assert q[
                "passage_path"
            ].is_file(), f"passage_path not found: {q['passage_path']}"
            assert q[
                "prompt_path"
            ].is_file(), f"prompt_path not found: {q['prompt_path']}"
            assert (
                q["passage_path"].read_text(encoding="utf-8").strip()
            ), f"empty passage content: {q['passage_path']}"
            assert (
                q["prompt_path"].read_text(encoding="utf-8").strip()
            ), f"empty prompt content: {q['prompt_path']}"


def _find_exam(university: str, year: int):
    for exam in SEED_EXAMS:
        if (
            exam.EXAM_META["university"] == university
            and exam.EXAM_META["year"] == year
        ):
            return exam
    raise AssertionError(f"Exam not registered: {university} {year}")


def test_cau_2025_questions_share_identical_passage():
    """CAU's real-exam parity: every question shows the full passage set."""
    cau = _find_exam("중앙대학교", 2025)
    texts = [q["passage_path"].read_text(encoding="utf-8") for q in cau.QUESTIONS]
    assert len(set(texts)) == 1, "CAU questions must share one passage text"


def test_inha_2026_q2_references_expected_graph_assets():
    """Q2 hybrid content must point at the five graph images the README
    asks the author to supply; missing references would break the layout."""
    inha = _find_exam("인하대학교", 2026)
    q2 = next(q for q in inha.QUESTIONS if q["question_number"] == 2)
    content = q2["passage_path"].read_text(encoding="utf-8")

    image_pattern = re.compile(r"/exam-assets/inha_2026_humanities/(q2_fig\d+\.png)")
    referenced = set(image_pattern.findall(content))
    expected = {f"q2_fig{i}.png" for i in range(1, 6)}
    assert (
        referenced == expected
    ), f"Q2 image refs mismatch. got={referenced}, want={expected}"


def test_inha_2026_q2_keeps_tables_as_markdown():
    """표 1/2/3 must stay as markdown pipe tables, not images — the LLM
    scoring agent reads cell values from the question.content string."""
    inha = _find_exam("인하대학교", 2026)
    q2 = next(q for q in inha.QUESTIONS if q["question_number"] == 2)
    content = q2["passage_path"].read_text(encoding="utf-8")

    for label in ("〈표 1〉", "〈표 2〉", "〈표 3〉"):
        assert label in content, f"{label} header not found in Q2 content"
    # Heuristic: each of 3 tables contributes >= 2 pipe-heavy lines.
    pipe_lines = sum(1 for line in content.splitlines() if line.count("|") >= 3)
    assert (
        pipe_lines >= 12
    ), f"Expected >=12 pipe-table lines for three tables, got {pipe_lines}"
