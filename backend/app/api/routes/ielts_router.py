import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette import status

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.models import DomainType
from app.crud import (
    essay_crud,
    example_essay_crud,
    feedback_crud,
    prompt_crud,
    rubric_crud,
)
from app.schemas import (
    essay_schema,
    example_essay_schema,
    feedback_schema,
    prompt_schema,
    rubric_criterion_schema,
)
from app.services import feedback_service

router = APIRouter()


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
async def prompt_create(prompt_in: prompt_schema.PromptCreate, db: SessionDep) -> None:
    await prompt_crud.create_prompt(db=db, prompt_create=prompt_in)


@router.get("/prompts", response_model=list[prompt_schema.Prompt])
async def get_prompts(db: SessionDep) -> list[prompt_schema.Prompt]:
    prompt_list = await prompt_crud.get_prompts(db, domain=DomainType.ielts)
    return prompt_list


@router.get("/example", response_model=example_essay_schema.ExampleEssay)
async def get_example_by_prompt_id(
    db: SessionDep, prompt_id: int
) -> example_essay_schema.ExampleEssay:
    example_essay = await example_essay_crud.get_example_essay_by_prompt_id(
        db, prompt_id
    )
    return example_essay


@router.get(
    "/criteria", response_model=list[rubric_criterion_schema.RubricCriterionPublic]
)
async def get_rubric_criteria(
    db: SessionDep, name: str
) -> list[rubric_criterion_schema.RubricCriterionPublic]:
    rubric = await rubric_crud.get_rubric_by_name(db, name)
    rubric_criteria = sorted(rubric.criteria, key=lambda x: x.id)

    return rubric_criteria


@router.get("/essays", response_model=list[essay_schema.EssayPublic])
async def get_essays_by_prompt_id(
    db: SessionDep, current_user: CurrentUser, prompt_id: int
) -> list[essay_schema.EssayPublic]:
    essay_list = await essay_crud.get_essay_list_by_prompt_id(
        db, current_user.id, prompt_id
    )
    return essay_list


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


@router.post("/essays/handwriting")
async def submit_handwriting_essay(
    db: SessionDep,
    current_user: CurrentUser,
    prompt_id: int,
    image: UploadFile = File(...),
) -> essay_schema.Essay:
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    contents = await image.read()
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
        )

    db_essay = await essay_crud.create_handwriting_essay(
        db, current_user.id, prompt_id, datetime.now(timezone.utc)
    )

    upload_dir = Path(settings.UPLOAD_DIR) / "essays" / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{db_essay.id}.png"
    await asyncio.to_thread(file_path.write_bytes, contents)

    await essay_crud.update_essay_image_path(db, db_essay.id, str(file_path))

    await db.refresh(db_essay)
    return essay_schema.Essay.model_validate(db_essay)


@router.get("/essays/{essay_id}/image")
async def get_essay_image(
    db: SessionDep, current_user: CurrentUser, essay_id: int
) -> FileResponse:
    essay = await essay_crud.get_essay_by_id(db, essay_id)
    if essay is None or essay.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Essay not found")
    if not essay.image_path or not os.path.isfile(essay.image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(essay.image_path, media_type="image/png")


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
    if essay.input_type.value == "handwriting":
        await feedback_service.generate_feedback_for_handwriting(
            db, current_user.id, essay_id, request
        )
    else:
        await feedback_service.generate_feedback(db, current_user.id, essay_id, request)
