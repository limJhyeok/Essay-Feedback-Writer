from datetime import datetime, timezone

from fastapi import APIRouter
from starlette import status

from app.api.deps import CurrentUser, SessionDep
from app.core import security
from app.crud import (
    ai_provider_crud,
    api_model_crud,
    bot_crud,
    essay_crud,
    example_essay_crud,
    feedback_crud,
    prompt_crud,
    rubric_crud,
    user_api_key_crud,
)
from app.schemas import (
    ai_provider_schema,
    api_model_schema,
    bot_schema,
    essay_schema,
    example_essay_schema,
    feedback_schema,
    prompt_schema,
    rubric_criterion_schema,
    user_api_key_schema,
)
from app.services import feedback_service

router = APIRouter()


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def prompt_create(prompt_in: prompt_schema.PromptCreate, db: SessionDep) -> None:
    prompt_crud.create_prompt(db=db, prompt_create=prompt_in)


@router.get("/prompts", response_model=list[prompt_schema.Prompt])
def get_prompts(db: SessionDep) -> list[prompt_schema.Prompt]:
    prompt_list = prompt_crud.get_prompts(db)
    return prompt_list


@router.get("/example", response_model=example_essay_schema.ExampleEssay)
def get_example_by_prompt_id(
    db: SessionDep, prompt_id: int
) -> example_essay_schema.ExampleEssay:
    example_essay = example_essay_crud.get_example_essay_by_prompt_id(db, prompt_id)
    return example_essay


@router.get(
    "/criteria", response_model=list[rubric_criterion_schema.RubricCriterionPublic]
)
def get_rubric_criteria(
    db: SessionDep, name: str
) -> list[rubric_criterion_schema.RubricCriterionPublic]:
    rubric = rubric_crud.get_rubric_by_name(db, name)
    rubric_criteria = sorted(rubric.criteria, key=lambda x: x.id)

    return rubric_criteria


@router.get("/essays", response_model=list[essay_schema.EssayPublic])
def get_essays_by_prompt_id(
    db: SessionDep, current_user: CurrentUser, prompt_id: int
) -> list[essay_schema.EssayPublic]:
    essay_list = essay_crud.get_essay_list_by_prompt_id(db, current_user.id, prompt_id)
    return essay_list


@router.get("/feedbacks", response_model=list[feedback_schema.FeedbackPublic])
def get_feedbacks_by_user_prompt(
    db: SessionDep, current_user: CurrentUser, prompt_id: int, essay_id: int
) -> list[feedback_schema.FeedbackPublic]:
    db_feedback_list = feedback_crud.get_feedbacks_by_user_prompt_essay(
        db, current_user.id, prompt_id, essay_id
    )
    feedback_list = []
    for fb in db_feedback_list:
        fb_public = feedback_schema.FeedbackPublic(
            bot_name=fb.bot.name, content=fb.content, created_at=fb.created_at
        )
        feedback_list.append(fb_public)
    return feedback_list


@router.get("/bots", response_model=list[bot_schema.BotPublic])
def read_bots(db: SessionDep) -> list[bot_schema.BotPublic]:
    return bot_crud.get_bots(db)


@router.get("/providers", response_model=list[ai_provider_schema.AIProviderPublic])
def read_providers(db: SessionDep) -> list[ai_provider_schema.AIProviderPublic]:
    return ai_provider_crud.get_providers(db)


@router.get(
    "/api_models/{provider_name}", response_model=list[api_model_schema.APIModelPublic]
)
def read_api_models(
    db: SessionDep, provider_name: str
) -> list[api_model_schema.APIModelPublic]:
    return api_model_crud.get_api_models_by_provider(db, provider_name)


@router.post("/essays")
def submit_essay(
    db: SessionDep, current_user: CurrentUser, request: essay_schema.EssayCreateRequest
) -> essay_schema.Essay:
    essay = essay_crud.get_duplicated_essay(
        db, current_user.id, request.prompt_id, request.content
    )
    if essay is None:
        essay_create = essay_schema.EssayCreate(
            user_id=current_user.id,
            prompt_id=request.prompt_id,
            content=request.content,
            submitted_at=datetime.now(),
        )
        essay = essay_crud.create_essay(db, essay_create)

    return essay


def generate_key_name():
    return f"secret-key_{datetime.now(timezone.utc).isoformat()}"


@router.post("/api_keys", status_code=status.HTTP_204_NO_CONTENT)
def create_api_key(
    db: SessionDep,
    current_user: CurrentUser,
    request: user_api_key_schema.UserAPIKeyCreateRequest,
):
    user_api_key_create = user_api_key_schema.UserAPIKeyCreate(
        user_id=current_user.id,
        provider_id=ai_provider_crud.get_provider_by_name(db, request.provider_name).id,
        name=request.name or generate_key_name(),
        api_key=security.encrypt_api_key(request.api_key),
    )
    _ = user_api_key_crud.create_user_api_key(db, user_api_key_create)


@router.get("/api_keys", response_model=list[user_api_key_schema.UserAPIKeyPublic])
def get_api_key_list(
    db: SessionDep, current_user: CurrentUser
) -> list[user_api_key_schema.UserAPIKeyPublic]:
    user_api_key_list = user_api_key_crud.get_user_api_key_list(db, current_user.id)
    response = []
    for user_api_key in user_api_key_list:
        item = user_api_key_schema.UserAPIKeyPublic(
            id=user_api_key.id,
            name=user_api_key.name,
            provider_name=user_api_key.provider.name,
            registered_at=user_api_key.registered_at,
            last_used=user_api_key.last_used,
            is_active=user_api_key.is_active,
        )
        response.append(item)

    return response


@router.put("/api_keys/{api_key_id}/name", status_code=status.HTTP_204_NO_CONTENT)
def rename_api_key(
    db: SessionDep,
    api_key_id: int,
    request: user_api_key_schema.UserAPIKeyRenameRequest,
) -> None:
    user_api_key_crud.update_api_key_name(db, api_key_id, request.name)


@router.delete("/api_keys/{api_key_id}")
def delete_api_key_route(db: SessionDep, api_key_id: int) -> None:
    user_api_key_crud.delete_api_key(db, api_key_id)


@router.post("/essays/{essay_id}/feedback")
async def trigger_feedback_generation(
    db: SessionDep,
    current_user: CurrentUser,
    essay_id: int,
    request: feedback_schema.FeedbackCreateRequest,
) -> None:
    feedback_service.generate_feedback(db, current_user.id, essay_id, request)
