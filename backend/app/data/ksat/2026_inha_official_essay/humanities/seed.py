"""Seed entry for 2026 Inha humanities mock essay.

Registered by app/data/ksat/seed_ksat_data.py. Unlike the CAU exams
which share one passage set across all questions, this exam has
independent passage sets per question (Q1: pure prose 제시문 (가)~(마);
Q2: `<다음>` claim block followed by 자료 1~6 mixing markdown tables and
graph image references).

Image assets for Q2 (fig1~fig5) must be placed under
`frontend/public/exam-assets/inha_2026_humanities/`. They are served as
static files by Vite; see README.md in that directory for filenames.
"""

from pathlib import Path

_EXAM_DIR = Path(__file__).parent

EXAM_META = {
    "university": "인하대학교",
    "year": 2026,
    "track": "humanities",
    "exam_type": "mock",
}

QUESTIONS = [
    {
        "question_number": 1,
        "passage_path": _EXAM_DIR / "passages" / "q_1.md",
        "prompt_path": _EXAM_DIR / "prompts" / "q_1.md",
        "example_answer_path": _EXAM_DIR / "example_answers" / "q_1.md",
        "max_points": 60,
        "char_min": 900,
        "char_max": 1100,
        "passage_refs": ["가", "나", "다", "라", "마"],
        "rubric_name": "KSAT 2026 Inha Humanities Q1",
    },
    {
        "question_number": 2,
        "passage_path": _EXAM_DIR / "passages" / "q_2.md",
        "prompt_path": _EXAM_DIR / "prompts" / "q_2.md",
        "example_answer_path": _EXAM_DIR / "example_answers" / "q_2.md",
        "max_points": 40,
        "char_min": 540,
        "char_max": 660,
        "passage_refs": [
            "다음",
            "자료1",
            "자료2",
            "자료3",
            "자료4",
            "자료5",
            "자료6",
        ],
        "rubric_name": "KSAT 2026 Inha Humanities Q2",
    },
]
