"""Seed entry for 2024 CAU humanities official essay.

Registered by app/data/ksat/seed_ksat_data.py. The registry loader reads
each question's passage/prompt/example_answer from the referenced paths
and populates ExamQuestion.content, Prompt.content, ExampleEssay.content.
"""

from pathlib import Path

_EXAM_DIR = Path(__file__).parent

EXAM_META = {
    "university": "중앙대학교",
    "year": 2024,
    "track": "humanities",
    "exam_type": "official",
}

QUESTIONS = [
    {
        "question_number": 1,
        "passage_path": _EXAM_DIR / "passages" / "q_1.md",
        "prompt_path": _EXAM_DIR / "prompts" / "q_1.md",
        "example_answer_path": _EXAM_DIR / "example_answers" / "q_1.md",
        "max_points": 40,
        "char_min": 550,
        "char_max": 570,
        "passage_refs": ["가", "나", "다", "라"],
        "rubric_name": "KSAT 2024 CAU Official Humanities Q1",
    },
    {
        "question_number": 2,
        "passage_path": _EXAM_DIR / "passages" / "q_2.md",
        "prompt_path": _EXAM_DIR / "prompts" / "q_2.md",
        "example_answer_path": _EXAM_DIR / "example_answers" / "q_2.md",
        "max_points": 40,
        "char_min": 550,
        "char_max": 570,
        "passage_refs": ["라", "마", "바", "사"],
        "rubric_name": "KSAT 2024 CAU Official Humanities Q2",
    },
    {
        "question_number": 3,
        "passage_path": _EXAM_DIR / "passages" / "q_3.md",
        "prompt_path": _EXAM_DIR / "prompts" / "q_3.md",
        "example_answer_path": _EXAM_DIR / "example_answers" / "q_3.md",
        "max_points": 20,
        "char_min": 330,
        "char_max": 350,
        "passage_refs": ["아", "자", "차"],
        "rubric_name": "KSAT 2024 CAU Official Humanities Q3",
    },
]
