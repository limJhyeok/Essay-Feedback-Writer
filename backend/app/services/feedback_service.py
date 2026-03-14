import asyncio
import base64
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.crud import (
    ai_provider_crud,
    api_model_crud,
    essay_crud,
    feedback_crud,
    prompt_crud,
    rubric_criterion_crud,
    user_api_key_crud,
)
from app.prompts.ielts_prompt import (
    IELTS_HOLISTIC_SYSTEM_PROMPT,
    IELTS_HUMAN_TEMPLATE,
    IELTS_SUB_SYSTEM_PROMPT,
    IELTS_SYSTEM_PROMPT_TEMPLATE,
)
from app.schemas import feedback_schema, user_api_key_schema


class FeedbackResponse(BaseModel):
    score: float
    feedback: str


_PROVIDER_MAP: dict[str, type[BaseChatModel]] = {
    "OpenAI": ChatOpenAI,
    "Anthropic": ChatAnthropic,
}


def get_llm_client(
    db_api_key: user_api_key_schema.UserAPIKey,
    provider_name: str,
    model_name: str,
) -> Runnable:
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
    system_prompt = IELTS_SYSTEM_PROMPT_TEMPLATE.format(
        criteria_name=criteria_name,
        subsystem_prompt=subsystem_prompt,
        rubric_for_criteria=rubric_for_criteria,
    )
    return system_prompt, IELTS_HUMAN_TEMPLATE


def get_llm_prompt_for_ielts_holistic_feedback(
    criteria_feedbacks: dict[str, str],
) -> tuple[str, str]:
    human_prompt = "Below are scores and feedback for four IELTS Writing Task 2 scoring criteria.\n"
    for criterion, text in criteria_feedbacks.items():
        human_prompt += f"\n### {criterion}\n{text}\n"
    human_prompt += "\nNow give the final score and your justification."
    return IELTS_HOLISTIC_SYSTEM_PROMPT, human_prompt


async def generate_feedback(
    db: AsyncSession,
    user_id: int,
    essay_id: int,
    request: feedback_schema.FeedbackCreateRequest,
    override_content: str | None = None,
) -> None:
    student_essay = await essay_crud.get_essay_by_id(db, essay_id)
    criterion_names = await rubric_criterion_crud.get_unique_criterion_names_by_rubric(
        db, request.rubric_name
    )

    db_provider = await ai_provider_crud.get_provider_by_name(
        db, request.model_provider_name
    )
    if db_provider is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown provider: {request.model_provider_name}",
        )
    db_api_key = await user_api_key_crud.get_user_api_key(db, user_id, db_provider.id)
    if db_api_key is None:
        raise HTTPException(
            status_code=404,
            detail=f"We couldn't find an active API key for {request.model_provider_name}. Please register your API key to proceed.",
        )
    structured_llm = get_llm_client(
        db_api_key, request.model_provider_name, request.api_model_name
    )

    feedback_response = {"feedback_by_criteria": {}}
    holistic_feedback_inputs: dict[str, str] = {}

    for criterion_name in criterion_names:
        criterion_list = await rubric_criterion_crud.get_criterion_by_name(
            db, criterion_name
        )
        rubric_text = "\n".join(
            f"- **{criterion.score}**: {criterion.description}"
            for criterion in criterion_list
        )
        system_prompt, human_template = get_llm_prompt_for_ielts(
            criterion_name, IELTS_SUB_SYSTEM_PROMPT.get(criterion_name, ""), rubric_text
        )
        essay_text = override_content or student_essay.content
        human_prompt = human_template.format(
            essay_prompt=request.prompt, student_essay=essay_text
        )

        result: FeedbackResponse = await structured_llm.ainvoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
        )

        feedback_response["feedback_by_criteria"][criterion_name] = {
            "score": result.score,
            "feedback": result.feedback,
        }

        holistic_feedback_inputs[criterion_name] = result.feedback

    holistic_system, holistic_human = get_llm_prompt_for_ielts_holistic_feedback(
        holistic_feedback_inputs
    )

    holistic_result: FeedbackResponse = await structured_llm.ainvoke(
        [SystemMessage(content=holistic_system), HumanMessage(content=holistic_human)]
    )

    feedback_response["overall_score"] = holistic_result.score
    feedback_response["overall_feedback"] = holistic_result.feedback

    api_model = await api_model_crud.get_api_model_by_name_and_provider(
        db, request.api_model_name, request.model_provider_name
    )
    prompt = await prompt_crud.get_prompt_by_content(db, request.prompt)
    feedback_create = feedback_schema.FeedbackCreate(
        user_id=user_id,
        prompt_id=prompt.id,
        essay_id=essay_id,
        bot_id=api_model.bot.id,
        content=feedback_response,
        created_at=datetime.now(timezone.utc),
    )

    await feedback_crud.create_feedback(db, feedback_create)
    await user_api_key_crud.update_last_used(db, db_api_key.id)


def get_vlm_client(
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
    return cls(model=model_name, api_key=decrypted_api_key)


async def generate_feedback_for_handwriting(
    db: AsyncSession,
    user_id: int,
    essay_id: int,
    request: feedback_schema.FeedbackCreateRequest,
) -> None:
    essay = await essay_crud.get_essay_by_id(db, essay_id)
    if not essay.image_path:
        raise HTTPException(status_code=400, detail="No image found for this essay")

    image_bytes = await asyncio.to_thread(Path(essay.image_path).read_bytes)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    db_provider = await ai_provider_crud.get_provider_by_name(
        db, request.model_provider_name
    )
    if db_provider is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown provider: {request.model_provider_name}",
        )
    db_api_key = await user_api_key_crud.get_user_api_key(db, user_id, db_provider.id)
    if db_api_key is None:
        raise HTTPException(
            status_code=404,
            detail=f"We couldn't find an active API key for {request.model_provider_name}. Please register your API key to proceed.",
        )

    vlm = get_vlm_client(
        db_api_key, request.model_provider_name, request.api_model_name
    )

    ocr_message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Transcribe ONLY the handwritten text visible in this image. Do NOT add, infer, or generate any text that is not explicitly written. If only a few words are written, output only those words. Preserve paragraph breaks. Output nothing besides the exact transcription.",
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_b64}"},
            },
        ]
    )
    response = await vlm.ainvoke([ocr_message])
    extracted_text = response.content

    await essay_crud.update_ocr_text(db, essay_id, extracted_text)

    await generate_feedback(
        db, user_id, essay_id, request, override_content=extracted_text
    )
