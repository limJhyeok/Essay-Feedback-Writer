from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.agents.loader import load_rubric
from app.api.deps import CurrentUser, SessionDep
from app.crud import (
    essay_crud,
    exam_crud,
    example_essay_crud,
    feedback_crud,
)
from app.schemas import (
    essay_schema,
    exam_schema,
    example_essay_schema,
    feedback_schema,
    prompt_schema,
    rubric_criterion_schema,
)
from app.services import feedback_service

router = APIRouter()


# ── Exam browsing ──────────────────────────────────────────────


@router.get("/exams", response_model=list[exam_schema.ExamPublic])
async def list_exams(
    db: SessionDep,
    university: Optional[str] = None,
    year: Optional[int] = None,
    track: Optional[str] = None,
) -> list[exam_schema.ExamPublic]:
    return await exam_crud.get_exams(db, university=university, year=year, track=track)


@router.get("/exams/{exam_id}", response_model=exam_schema.ExamDetailPublic)
async def get_exam(db: SessionDep, exam_id: int) -> exam_schema.ExamDetailPublic:
    exam = await exam_crud.get_exam_by_id(db, exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.get(
    "/exams/{exam_id}/questions", response_model=list[exam_schema.ExamQuestionPublic]
)
async def get_questions(
    db: SessionDep, exam_id: int
) -> list[exam_schema.ExamQuestionPublic]:
    return await exam_crud.get_questions_by_exam_id(db, exam_id)


# ── Prompts (KSAT domain only) ────────────────────────────────


@router.get("/prompts", response_model=list[prompt_schema.Prompt])
async def get_ksat_prompts(db: SessionDep) -> list[prompt_schema.Prompt]:
    return await exam_crud.get_ksat_prompts(db)


# ── Essays ─────────────────────────────────────────────────────


@router.post("/essays")
async def submit_essay(
    db: SessionDep, current_user: CurrentUser, request: essay_schema.EssayCreateRequest
) -> essay_schema.Essay:
    essay = await essay_crud.get_duplicated_essay(
        db, current_user.id, request.prompt_id, request.content
    )
    if essay is None:
        essay_create = essay_schema.EssayCreate(
            user_id=current_user.id,
            prompt_id=request.prompt_id,
            content=request.content,
            submitted_at=datetime.now(),
        )
        essay = await essay_crud.create_essay(db, essay_create)
    return essay


@router.get("/essays", response_model=list[essay_schema.EssayPublic])
async def get_essays_by_prompt_id(
    db: SessionDep, current_user: CurrentUser, prompt_id: int
) -> list[essay_schema.EssayPublic]:
    return await essay_crud.get_essay_list_by_prompt_id(db, current_user.id, prompt_id)


# ── Feedback ───────────────────────────────────────────────────


@router.post("/essays/{essay_id}/feedback")
async def trigger_feedback_generation(
    db: SessionDep,
    current_user: CurrentUser,
    essay_id: int,
    request: feedback_schema.FeedbackCreateRequest,
) -> None:
    essay = await essay_crud.get_essay_by_id(db, essay_id)
    if essay is None:
        raise HTTPException(status_code=404, detail="Essay not found")
    await feedback_service.generate_feedback(db, current_user.id, essay_id, request)


@router.get("/feedbacks", response_model=list[feedback_schema.FeedbackPublic])
async def get_feedbacks_by_user_prompt(
    db: SessionDep, current_user: CurrentUser, prompt_id: int, essay_id: int
) -> list[feedback_schema.FeedbackPublic]:
    db_feedback_list = await feedback_crud.get_feedbacks_by_user_prompt_essay(
        db, current_user.id, prompt_id, essay_id
    )
    feedback_list = []
    for fb in db_feedback_list:
        fb_public = feedback_schema.FeedbackPublic(
            bot_name=fb.bot.name, content=fb.content, created_at=fb.created_at
        )
        feedback_list.append(fb_public)
    return feedback_list


# ── Criteria & Example ─────────────────────────────────────────


@router.get(
    "/criteria", response_model=list[rubric_criterion_schema.RubricCriterionPublic]
)
async def get_rubric_criteria(
    name: str,
) -> list[rubric_criterion_schema.RubricCriterionPublic]:
    try:
        rubric_spec = load_rubric(rubric_name=name)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Rubric '{name}' not found")
    return [
        rubric_criterion_schema.RubricCriterionPublic(
            name=c.name,
            description=c.description,
            score=c.scale_max,
        )
        for c in rubric_spec.criteria
    ]


@router.get("/example", response_model=example_essay_schema.ExampleEssay)
async def get_example_by_prompt_id(
    db: SessionDep, prompt_id: int
) -> example_essay_schema.ExampleEssay:
    return await example_essay_crud.get_example_essay_by_prompt_id(db, prompt_id)
