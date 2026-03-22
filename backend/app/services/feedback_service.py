import asyncio
import base64
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.aggregator import Aggregator
from app.agents.builder import generate_aggregator_agent, generate_criterion_agents
from app.agents.loader import load_rubric
from app.agents.schema import CriterionResult, ScoringResult
from app.agents.swarm import ScoringSwarm
from app.core import security
from app.crud import (
    ai_provider_crud,
    api_model_crud,
    essay_crud,
    feedback_crud,
    prompt_crud,
    user_api_key_crud,
)
from app.schemas import feedback_schema, user_api_key_schema


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
    return llm.with_structured_output(CriterionResult)


def _scoring_result_to_jsonb(result: ScoringResult) -> dict:
    return {
        "feedback_by_criteria": {
            cr.name: {"score": cr.score, "feedback": cr.feedback}
            for cr in result.criteria
        },
        "overall_score": result.overall_score,
        "overall_feedback": result.overall_feedback,
    }


async def generate_feedback(
    db: AsyncSession,
    user_id: int,
    essay_id: int,
    request: feedback_schema.FeedbackCreateRequest,
    override_content: str | None = None,
) -> None:
    student_essay = await essay_crud.get_essay_by_id(db, essay_id)

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

    # Load rubric from YAML config
    rubric = load_rubric(rubric_name=request.rubric_name)

    # Build criterion agents and score in parallel
    criterion_agents = generate_criterion_agents(rubric)
    swarm = ScoringSwarm(structured_llm)
    swarm.add_agents(criterion_agents)

    essay_text = override_content or student_essay.content
    criteria_results = await swarm.score(
        essay_prompt=request.prompt, student_essay=essay_text
    )

    # Aggregate results
    aggregator_agent = generate_aggregator_agent(rubric)
    aggregator = Aggregator(rubric, structured_llm)
    scoring_result = await aggregator.aggregate(criteria_results, aggregator_agent)

    # Convert to JSONB format and store
    feedback_response = _scoring_result_to_jsonb(scoring_result)

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
