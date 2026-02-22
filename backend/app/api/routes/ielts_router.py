from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from starlette import status

from app.core import security
from app.api.deps import SessionDep, CurrentUser
from app.crud import (
    prompt_crud,
    essay_crud,
    feedback_crud,
    bot_crud,
    example_essay_crud,
    rubric_crud,
    rubric_criterion_crud,
    api_model_crud,
    user_api_key_crud,
    ai_provider_crud,
)
from app.schemas import (
    prompt_schema,
    essay_schema,
    feedback_schema,
    example_essay_schema,
    rubric_criterion_schema,
    bot_schema,
    api_model_schema,
    user_api_key_schema,
    ai_provider_schema,
)

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


class FeedbackResponse(BaseModel):
    score: float
    feedback: str


@router.post("/essays/{essay_id}/feedback")
async def trigger_feedback_generation(
    db: SessionDep,
    current_user: CurrentUser,
    essay_id: int,
    request: feedback_schema.FeedbackCreateRequest,
) -> None:
    student_essay = essay_crud.get_essay_by_id(db, essay_id)
    criterion_names = rubric_criterion_crud.get_unique_criterion_names_by_rubric(
        db, request.rubric_name
    )

    sub_system_prompts = {
        "Task Response": """Use the rubric below to assess how well the essay addresses the prompt. Pay close attention to:
- Whether the essay clearly answers the question
- How well-developed and supported the ideas are
- Relevance and extension of the content
""",
        "Coherence & Cohesion": """Use the rubric below to assess how well the essay is organised and how ideas flow logically. Pay attention to:
- The logical organisation of ideas and the progression of arguments
- The use of cohesive devices (e.g., linking words, paragraphing) to make the essay easy to follow
- The clarity and fluency of paragraphing
""",
        "Lexical Resource": """Use the rubric below to assess the range and accuracy of vocabulary used in the essay. Pay attention to:
- The range of vocabulary used and how appropriate and varied it is
- The accuracy of word choice, including collocations and precision
- Whether there are any noticeable errors in spelling, word form, or word choice that affect understanding
""",
        "Grammatical Range & Accuracy": """Use the rubric below to assess the range and accuracy of grammar used in the essay. Pay attention to:
- The variety of sentence structures used (simple, compound, complex)
- The accuracy of grammar, including verb tenses, subject-verb agreement, punctuation, and article use
- Whether errors in grammar hinder communication or understanding
""",
    }
    db_provider = ai_provider_crud.get_provider_by_name(db, request.model_provider_name)
    db_api_key = user_api_key_crud.get_user_api_key(db, current_user.id, db_provider.id)
    if db_api_key is None:
        raise HTTPException(
            status_code=404,
            detail=f"We couldn’t find an active API key for {request.model_provider_name}. Please register your API key to proceed.",
        )
    structured_llm = get_llm_client(
        db, db_api_key, request.model_provider_name, request.api_model_name
    )

    feedback_response = {"feedback_by_criteria": {}}
    holistic_feedback_inputs = {}

    for criterion_name in criterion_names:
        criterion_list = rubric_criterion_crud.get_criterion_by_name(db, criterion_name)
        rubric_text = "\n".join(
            f"- **{criterion.score}**: {criterion.description}"
            for criterion in criterion_list
        )
        system_prompt, human_template = get_llm_prompt_for_ielts(
            criterion_name, sub_system_prompts.get(criterion_name, ""), rubric_text
        )
        human_prompt = human_template.format(
            essay_prompt=request.prompt, student_essay=student_essay.content
        )

        result: FeedbackResponse = structured_llm.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
        )

        feedback_response["feedback_by_criteria"][criterion_name] = {
            "score": result.score,
            "feedback": result.feedback,
        }

        holistic_feedback_inputs[criterion_name] = result.feedback

    holistic_system, holistic_human = get_llm_prompt_for_ielts_holistic_feedback(
        **holistic_feedback_inputs
    )

    holistic_result: FeedbackResponse = structured_llm.invoke(
        [SystemMessage(content=holistic_system), HumanMessage(content=holistic_human)]
    )

    feedback_response["overall_score"] = holistic_result.score
    feedback_response["overall_feedback"] = holistic_result.feedback

    api_model = api_model_crud.get_api_model_by_name_and_provider(
        db, request.api_model_name, request.model_provider_name
    )
    prompt = prompt_crud.get_prompt_by_content(db, request.prompt)
    feedback_create = feedback_schema.FeedbackCreate(
        user_id=current_user.id,
        prompt_id=prompt.id,
        essay_id=essay_id,
        bot_id=api_model.bot.id,
        content=feedback_response,
        created_at=datetime.now(),
    )

    _ = feedback_crud.create_feedback(db, feedback_create)
    user_api_key_crud.update_last_used(db, db_api_key.id)


_PROVIDER_MAP: dict[str, type[BaseChatModel]] = {
    "OpenAI": ChatOpenAI,
    "Anthropic": ChatAnthropic,
}


def get_llm_client(
    db: SessionDep,
    db_api_key: user_api_key_schema.UserAPIKey,
    provider_name: str,
    model_name: str,
) -> BaseChatModel:
    cls = _PROVIDER_MAP.get(provider_name)
    if cls is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider: {provider_name}",
        )

    decrypted_api_key = security.decrypt_api_key(db_api_key.api_key)
    llm = cls(model=model_name, api_key=decrypted_api_key)
    return llm.with_structured_output(FeedbackResponse)


def get_llm_prompt_for_ielts(
    criteria_name: str, subsystem_prompt: str, rubric_for_criteria: str
) -> tuple[str, str]:
    system_prompt = f"""You are a professional IELTS writing examiner. Your job is to evaluate essays written in response to specific prompts. You assess essays based on a rubric with scores from 0 to 9. Each score corresponds to a specific level of performance on the "{criteria_name}" criteria.

    {subsystem_prompt}

    Assign a **score between 0 and 9** based on the closest match in the rubric and provide a brief explanation justifying your score. Then give **constructive feedback** with suggestions for improvement.

    **Evaluation Criteria**: {criteria_name}

    **Rubric for "{criteria_name}"**:
    {rubric_for_criteria}
    """
    human_template = """**Essay Prompt**:
    {essay_prompt}

    **Student's Essay**:
    {student_essay}"""
    return system_prompt, human_template


def get_llm_prompt_for_ielts_holistic_feedback(**kwargs):
    system_prompt = """You are an IELTS examiner.

Your job is to:
1. Calculate the average band score based on the four criteria.
2. Provide the final overall score (rounded to the nearest half band).
3. Justify the final band score in 2-3 sentences.
4. Do not repeat the individual criteria feedback — just summarise holistically."""
    human_prompt = "Below are scores and feedback for four IELTS Writing Task 2 scoring criteria.\n"
    for criterion, text in kwargs.items():
        human_prompt += f"\n### {criterion}\n{text}\n"
    human_prompt += "\nNow give the final score and your justification."
    return system_prompt, human_prompt
