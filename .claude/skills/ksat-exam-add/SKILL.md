---
name: ksat-exam-add
description: Add a new KSAT (수능·대학 논술) essay dataset — passages, prompts, example answers, grading manual, seed.py, rubric YAMLs — and wire them into the seed/rubric registries. Use when the user provides a new 논술 problem PDF/source (e.g. "2027 XXX대학교 모의논술 추가해줘") or asks to extend KSAT coverage.
---

# Adding a New KSAT Essay Dataset

End-to-end recipe for introducing a new KSAT essay into the system. Follow these steps in order — each step builds on the previous one.

## Naming Conventions

- **Exam directory**: `backend/app/data/ksat/{year}_{univ_slug}_{exam_type}_essay/{track}/`
  - `year`: 학년도 (e.g. `2024`, `2026`)
  - `univ_slug`: 영문 약어 소문자 (e.g. `cau`, `inha`, `skku`)
  - `exam_type`: `mock` (모의논술) 또는 `official` (본고사)
  - `track`: `humanities` (인문사회) 또는 `sciences` (자연계)
- **Rubric YAML**: `backend/app/agents/configs/ksat/{univ_slug}_{year}_{exam_type?}_{track}_q{N}.yaml`
  - For mocks, `exam_type` segment is omitted: `cau_2024_humanities_q1.yaml`
  - For officials, include it: `cau_2024_official_humanities_q1.yaml`
- **Rubric registry name**: `"KSAT {year} {Univ} [Official] {Track_Titlecase} Q{N}"`
  - Mock: `"KSAT 2024 CAU Humanities Q1"`
  - Official: `"KSAT 2024 CAU Official Humanities Q1"`
  - Inha 2026: `"KSAT 2026 Inha Humanities Q1"`

## Step-by-Step Process

### Step 1 — Create the directory skeleton

```
backend/app/data/ksat/{year}_{univ}_{type}_essay/{track}/
├── passages/          q_1.md, q_2.md, q_3.md …
├── prompts/           q_1.md, q_2.md, q_3.md …
├── example_answers/   q_1.md, q_2.md, q_3.md …
├── grading_manual.md
├── seed.py
└── <source PDFs>      (문제지 + 채점매뉴얼; keep for audit)
```

Create subdirs with `mkdir -p`.

### Step 2 — Populate passage files

Two layout conventions exist:

- **Shared-passages (CAU pattern)**: all `q_{N}.md` files contain the **same full passage set** (가)~(차). Duplicated, yes, but each `ExamQuestion.content` record is self-contained.
- **Per-question passages (Inha pattern)**: each `q_{N}.md` holds only that question's passage subset.

Pick based on the source exam. If one passage set backs multiple prompts, use the CAU pattern.

Formatting rules for the passage file:
- Start with `다음 글을 읽고 물음에 답하시오.` if that's how the PDF reads.
- Keep passage markers `**(가)**`, `**(나)**` … bolded.
- Preserve original line breaks from the PDF (don't reflow).
- Keep footnotes marked with `*` (e.g. `*관격 : ...`) inline where the PDF places them.
- Use `---` (markdown HR) between passages when visually helpful.

### Step 3 — Populate prompt files

One prompt per question, **body only**:

- ❌ Do NOT include: `[문제 1]` prefix, `[40점, 550-570자]` annotation, trailing punctuation like `.`
- ✅ Do include: full prompt sentence ending with `…서술하시오.` / `…논술하시오.`
- One file per question: `prompts/q_1.md`, `prompts/q_2.md`, …

### Step 4 — Populate example answer files

One file per question, **answer body only**:

- ❌ Strip duplicated prompt text at the top (e.g. `"[문제 1] …서술하시오. [40점, …]"`)
- ❌ Strip trailing character-count annotation like `(570자)`
- ✅ Keep the answer text only, ending with a period

### Step 5 — Write `grading_manual.md`

Use the existing format (see `2026_inha_mock_essay/humanities/grading_manual.md` or `2025_cau_mock_essay/humanities/grading_manual.md` for reference). Required sections:

1. **제시문 출전과 해설** — markdown table (제시문 | 출전 | 교과서) + brief per-passage paragraphs
2. **예시 답안** — links to `example_answers/q_{N}.md`
3. **채점 기준** — per-question subsections with:
   - 기술적 측면 감점 표 (글자 수 위반, 맞춤법, 제시문 그대로 옮겨 쓴 경우)
   - 내용적 측면 세부 기준과 배점
   - 배점 가이드 (상/중/하 범위)

This manual is **documentation only** — it is NOT loaded at runtime. The authoritative rubric is the YAML (Step 7).

### Step 6 — Write `seed.py`

Template:

```python
"""Seed entry for {year} {Univ} {track} {exam_type} essay.

Registered by app/data/ksat/seed_ksat_data.py. The registry loader reads
each question's passage/prompt/example_answer from the referenced paths
and populates ExamQuestion.content, Prompt.content, ExampleEssay.content.
"""

from pathlib import Path

_EXAM_DIR = Path(__file__).parent

EXAM_META = {
    "university": "중앙대학교",            # Korean full name
    "year": 2024,                           # int, 학년도
    "track": "humanities",                  # "humanities" or "sciences"
    "exam_type": "mock",                    # "mock" or "official"
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
        "passage_refs": ["가", "나", "다", "라"],   # which subpassages THIS question cites
        "rubric_name": "KSAT 2024 CAU Humanities Q1",
    },
    # … q_2, q_3
]
```

Verify:
- `max_points` matches the grading manual's 만점
- `char_min` / `char_max` match the prompt's 글자 수 range
- `passage_refs` lists the Korean syllable markers that THIS question actually cites (read the prompt text — e.g. Q1 says "제시문 (가), (나), (다), (라)에서…" → `["가","나","다","라"]`)
- `rubric_name` must be unique and match the registry key you'll add in Step 8

### Step 7 — Create rubric YAML(s)

One YAML per question under `backend/app/agents/configs/ksat/`. Choose aggregation:

- **`weighted_sum`** (RECOMMENDED): each criterion's `scale_max` literally contributes its max points to the overall. Use when `Σ scale_max == overall_scale_max`. Set `weight: 1.0` on all criteria. This is the Inha 2026 / CAU 2024 Official pattern.
- **`weighted_average`**: legacy pattern used by 2025 CAU and 2024 CAU mocks. Formula: `Σ(score × weight) / Σ weight`. Note: **does NOT automatically normalize to `overall_scale_max`** — if criteria have `scale_max` other than 1.0, the max achievable score won't equal `overall_scale_max`. Avoid for new rubrics unless matching legacy.

Template (weighted_sum):

```yaml
name: "KSAT 2024 CAU Official Humanities Q1"
description: "2024 중앙대학교 인문사회계열 본고사 논술 문제 1 채점 기준 (40점 만점)"
lang: "ko"
overall_scale_min: 0
overall_scale_max: 40
aggregation: "weighted_sum"
rounding: "integer"

system_prompt_template: |
  당신은 대한민국 대학 논술 시험 채점 전문가입니다. …

  평가 기준: "{criteria_name}"

  {guidance}

  아래 채점 기준표에 따라 점수를 부여하고, 점수의 근거를 구체적으로 설명하세요. …

  **채점 기준표**:
  {band_descriptors}

human_prompt_template: |
  **문제**:
  {원본 프롬프트 그대로, 점수·글자 수 annotation 포함}

  **학생 답안**:
  {student_essay}

aggregator_system_prompt: |
  당신은 대학 논술 시험 채점관입니다.
  채점 결과를 종합하여: …

criteria:
  - name: "내용 이해"
    description: "… (N점)"
    weight: 1.0
    scale_min: 0
    scale_max: 32        # 이 criterion 의 만점 = 내용적 측면 점수
    guidance: |
      각 제시문에서 평가 기준 …
      배점 가이드:
      - 4개 제시문 모두 서술: 25~32점
      - …
    band_descriptors:
      32: "설명 텍스트"
      24: "…"
      # 보통 4~5개 band (scale_max, 중간, 하위, 0)

  - name: "논리적 구성"
    weight: 1.0
    scale_min: 0
    scale_max: 8
    guidance: | …
    band_descriptors: { 8: …, 5: …, 3: …, 0: … }

  - name: "기술적 감점"
    description: "… (최대 -N점, 0이 최고점)"
    weight: 1.0
    scale_min: -10        # 감점 허용 범위 (weighted_sum에서 clamp로 보호됨)
    scale_max: 0
    guidance: |
      감점만 적용 (0이 최고점).
      - 글자 수 위반 (기준 {CHAR_MIN}-{CHAR_MAX}자): ±1~25자 = -1점, ±26자 이상 = -2점
      - 맞춤법/원고지 사용법 중대한 오류: 최대 -3점
      - 제시문을 한 문장 이상 그대로 옮겨 쓴 경우: 최대 -5점
    band_descriptors: { 0: …, -2: …, -5: …, -10: … }
```

Rules of thumb:
- **Positive scale_max values must sum to `overall_scale_max`** for weighted_sum (not counting 기술적 감점 which has scale_max=0).
- **기술적 감점** is always a dedicated criterion with `scale_min < 0` and `scale_max: 0` — the `weighted_sum` clamp in `aggregator.py` prevents going below `overall_scale_min`.
- Use `guidance` to spell out per-passage expected answer contents (차이점/이유/근거 등) so the scoring agent has concrete hooks.
- `band_descriptors` keys are integer scores. Provide 4-6 bands spanning scale_min..scale_max.

### Step 8 — Register the rubric name in `loader.py`

Add an entry to `_RUBRIC_REGISTRY` in `backend/app/agents/loader.py`:

```python
_RUBRIC_REGISTRY: dict[str, str] = {
    # … existing entries …
    "KSAT 2024 CAU Official Humanities Q1": "ksat/cau_2024_official_humanities_q1.yaml",
    "KSAT 2024 CAU Official Humanities Q2": "ksat/cau_2024_official_humanities_q2.yaml",
    "KSAT 2024 CAU Official Humanities Q3": "ksat/cau_2024_official_humanities_q3.yaml",
}
```

**Key must exactly match the `rubric_name` in seed.py's QUESTIONS list.**

### Step 9 — Register the seed module in `seed_ksat_data.py`

Append to `SEED_EXAMS` in `backend/app/data/ksat/seed_ksat_data.py`:

```python
SEED_EXAMS: list[ModuleType] = [
    # … existing entries …
    _load_seed(_BASE / "2024_cau_official_essay" / "humanities" / "seed.py"),
]
```

### Step 10 — Verify everything loads

Run inside the backend container:

```bash
docker-compose exec -T backend python -c "
from app.agents.loader import load_rubric
from app.data.ksat.seed_ksat_data import SEED_EXAMS

# 1. Rubrics
for name in ['KSAT 2024 CAU Official Humanities Q1', 'KSAT 2024 CAU Official Humanities Q2', 'KSAT 2024 CAU Official Humanities Q3']:
    r = load_rubric(rubric_name=name)
    pos = sum(c.scale_max for c in r.criteria if c.scale_max > 0)
    print(f'{name}: aggregation={r.aggregation.value}, overall=[{r.overall_scale_min},{r.overall_scale_max}], +sum={pos}')

# 2. Seeds
for m in SEED_EXAMS:
    meta = m.EXAM_META
    print(f\"{meta['year']} {meta['university']} ({meta['track']}, {meta['exam_type']}): {len(m.QUESTIONS)} Qs\")
"
```

Expected output:
- Each rubric loads without error
- `+sum == overall_scale_max` (for weighted_sum rubrics)
- Seed prints question count matching your seed.py

### Step 11 — Seed the database

The seed loader is invoked by `backend/app/initial_data.py` / `core/db.py` at app startup. To apply new seeds to the running dev DB, either:

```bash
# Option A: restart backend (triggers init_db on boot)
docker-compose restart backend

# Option B: run the seeder directly (if exposed as a CLI)
docker-compose exec backend python -m app.initial_data
```

Confirm the new exam appears via:

```bash
docker-compose exec -T backend python -c "
from sqlalchemy import select
from app.core.db import async_session
from app.models import Exam
import asyncio
async def q():
    async with async_session() as s:
        rows = (await s.execute(select(Exam).order_by(Exam.year))).scalars().all()
        for e in rows:
            print(e.year, e.university, e.track, e.exam_type)
asyncio.run(q())
"
```

## Common Pitfalls

- **Rubric name mismatch** between `seed.py` and `loader.py`: loader raises `ValueError: Unknown rubric: …` at scoring time. Always keep the two in sync.
- **Mock rubric reused for official exam**: mock rubrics' `guidance`/`band_descriptors` reference mock-specific passage content. Reusing them on an official exam produces nonsense feedback. **Always create a separate rubric for each distinct passage set.**
- **`passage_refs` wrong**: must match the Korean markers cited in the prompt (e.g. Q2 prompt says "제시문 (라), (마), (바)" → refs `["라","마","바"]`, not Q1's refs).
- **`max_points` / `char_min` / `char_max` off-by-one**: double-check against the prompt's `[N점, NNN-NNN자]` annotation in the source PDF.
- **`exam_type` vs directory name**: dir is `2024_cau_official_essay` → seed.py must have `"exam_type": "official"`. Do not copy-paste from a mock seed without updating both the docstring and this field.
- **Weighted_average caveat**: with non-uniform `weight`/`scale_max`, max achievable score rarely equals `overall_scale_max` — the legacy CAU 2025 / CAU 2024 mock rubrics have this shape. Prefer `weighted_sum` for new rubrics.

## Reference Examples in This Repo

- `backend/app/data/ksat/2026_inha_mock_essay/humanities/` — per-question passages, weighted_sum rubrics
- `backend/app/data/ksat/2025_cau_mock_essay/humanities/` — shared-passages, weighted_average rubrics
- `backend/app/data/ksat/2024_cau_official_essay/humanities/` — shared-passages, weighted_sum rubrics (official-exam-specific rubrics with `Official` in the registry name)
- `backend/app/agents/configs/ksat/inha_2026_humanities_q1.yaml` — full weighted_sum YAML with deduction criterion

## Quick Checklist

```
[ ] backend/app/data/ksat/{year}_{univ}_{type}_essay/{track}/ created with passages/, prompts/, example_answers/
[ ] passage files populated (shared-set or per-question pattern chosen)
[ ] prompts cleaned (no [문제 N] prefix, no [N점, …] annotation)
[ ] example answers cleaned (no duplicated prompt at top, no (N자) at end)
[ ] grading_manual.md written
[ ] seed.py: EXAM_META + QUESTIONS with correct passage_refs, max_points, char_min/max, rubric_name
[ ] rubric YAML(s) created under backend/app/agents/configs/ksat/
[ ]   Σ(positive scale_max) == overall_scale_max for weighted_sum
[ ]   기술적 감점 criterion has scale_min<0, scale_max=0
[ ] loader.py _RUBRIC_REGISTRY updated with every rubric_name
[ ] seed_ksat_data.py SEED_EXAMS updated
[ ] verification script passes (all rubrics load, seed prints correct counts)
[ ] backend restarted to re-seed DB
```
