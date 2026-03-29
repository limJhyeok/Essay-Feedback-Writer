from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.agents.schema import CriterionResult, ScoringResult
from app.services.feedback_service import (
    _scoring_result_to_jsonb,
    generate_feedback,
    generate_feedback_for_handwriting,
    get_llm_client,
)


def _make_mock_api_key():
    """Create a mock UserAPIKey DB object."""
    mock = MagicMock()
    mock.api_key = "encrypted_fake_key"
    mock.id = 1
    return mock


def _make_request(**overrides):
    """Create a mock FeedbackCreateRequest."""
    mock = MagicMock()
    mock.model_provider_name = overrides.get("provider", "OpenAI")
    mock.api_model_name = overrides.get("model", "gpt-4o")
    mock.rubric_name = overrides.get("rubric", "IELTS Writing Task 2")
    mock.prompt = overrides.get("prompt", "Write about climate change")
    return mock


# ---------------------------------------------------------------------------
# get_llm_client tests
# ---------------------------------------------------------------------------


def test_get_llm_client_unsupported_provider_raises_400():
    """get_llm_client with unknown provider should raise HTTP 400."""
    mock_api_key = _make_mock_api_key()

    with pytest.raises(HTTPException) as exc_info:
        get_llm_client(mock_api_key, "NonExistentProvider", "some-model")

    assert exc_info.value.status_code == 400
    assert "Unsupported provider" in exc_info.value.detail


@patch("app.services.feedback_service.security.decrypt_api_key", return_value="sk-fake")
def test_get_llm_client_openai_creates_chat_openai(mock_decrypt):
    """'OpenAI' provider should instantiate ChatOpenAI with correct params."""
    mock_api_key = _make_mock_api_key()
    mock_cls = MagicMock()
    mock_llm = MagicMock()
    mock_cls.return_value = mock_llm

    with patch.dict(
        "app.services.feedback_service._PROVIDER_MAP", {"OpenAI": mock_cls}
    ):
        get_llm_client(mock_api_key, "OpenAI", "gpt-4o")

    mock_decrypt.assert_called_once_with("encrypted_fake_key")
    mock_cls.assert_called_once_with(model="gpt-4o", api_key="sk-fake")


@patch("app.services.feedback_service.security.decrypt_api_key", return_value="sk-fake")
def test_get_llm_client_anthropic_creates_chat_anthropic(mock_decrypt):
    """'Anthropic' provider should instantiate ChatAnthropic with correct params."""
    mock_api_key = _make_mock_api_key()
    mock_cls = MagicMock()
    mock_llm = MagicMock()
    mock_cls.return_value = mock_llm

    with patch.dict(
        "app.services.feedback_service._PROVIDER_MAP", {"Anthropic": mock_cls}
    ):
        get_llm_client(mock_api_key, "Anthropic", "claude-sonnet-4-5")

    mock_decrypt.assert_called_once_with("encrypted_fake_key")
    mock_cls.assert_called_once_with(model="claude-sonnet-4-5", api_key="sk-fake")


@patch("app.services.feedback_service.security.decrypt_api_key", return_value="sk-fake")
def test_get_llm_client_returns_structured_output(mock_decrypt):
    """get_llm_client should return llm.with_structured_output(CriterionResult)."""
    mock_api_key = _make_mock_api_key()
    mock_cls = MagicMock()
    mock_llm = MagicMock()
    mock_cls.return_value = mock_llm
    mock_structured = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured

    with patch.dict(
        "app.services.feedback_service._PROVIDER_MAP", {"OpenAI": mock_cls}
    ):
        result = get_llm_client(mock_api_key, "OpenAI", "gpt-4o")

    mock_llm.with_structured_output.assert_called_once_with(CriterionResult)
    assert result is mock_structured


# ---------------------------------------------------------------------------
# _scoring_result_to_jsonb tests
# ---------------------------------------------------------------------------


def test_scoring_result_to_jsonb_basic():
    """_scoring_result_to_jsonb should produce the expected dict shape."""
    result = ScoringResult(
        overall_score=6.5,
        overall_feedback="Solid essay.",
        criteria=[
            CriterionResult(name="Task Response", score=7.0, feedback="Good"),
            CriterionResult(name="Lexical Resource", score=6.0, feedback="OK"),
        ],
    )
    jsonb = _scoring_result_to_jsonb(result)

    assert jsonb["overall_score"] == 6.5
    assert jsonb["overall_feedback"] == "Solid essay."
    assert "Task Response" in jsonb["feedback_by_criteria"]
    assert jsonb["feedback_by_criteria"]["Task Response"] == {
        "score": 7.0,
        "feedback": "Good",
    }
    assert jsonb["feedback_by_criteria"]["Lexical Resource"] == {
        "score": 6.0,
        "feedback": "OK",
    }


def test_scoring_result_to_jsonb_empty_criteria():
    """_scoring_result_to_jsonb with no criteria should return empty dict for feedback_by_criteria."""
    result = ScoringResult(
        overall_score=5.0,
        overall_feedback="No criteria.",
        criteria=[],
    )
    jsonb = _scoring_result_to_jsonb(result)

    assert jsonb["feedback_by_criteria"] == {}
    assert jsonb["overall_score"] == 5.0
    assert jsonb["overall_feedback"] == "No criteria."


# ---------------------------------------------------------------------------
# generate_feedback error path tests
# ---------------------------------------------------------------------------


@patch(
    "app.services.feedback_service.ai_provider_crud.get_provider_by_name",
    new_callable=AsyncMock,
    return_value=None,
)
@patch(
    "app.services.feedback_service.essay_crud.get_essay_by_id",
    new_callable=AsyncMock,
    return_value=MagicMock(),
)
async def test_generate_feedback_unknown_provider_raises_404(mock_essay, mock_provider):
    """generate_feedback should raise HTTP 404 when provider is not found."""
    db = MagicMock()
    request = _make_request(provider="UnknownProvider")

    with pytest.raises(HTTPException) as exc_info:
        await generate_feedback(db, user_id=1, essay_id=1, request=request)

    assert exc_info.value.status_code == 404
    assert "UnknownProvider" in exc_info.value.detail


@patch(
    "app.services.feedback_service.user_api_key_crud.get_user_api_key",
    new_callable=AsyncMock,
    return_value=None,
)
@patch(
    "app.services.feedback_service.ai_provider_crud.get_provider_by_name",
    new_callable=AsyncMock,
    return_value=MagicMock(id=1),
)
@patch(
    "app.services.feedback_service.essay_crud.get_essay_by_id",
    new_callable=AsyncMock,
    return_value=MagicMock(),
)
async def test_generate_feedback_missing_api_key_raises_404(
    mock_essay, mock_provider, mock_api_key
):
    """generate_feedback should raise HTTP 404 when user has no API key."""
    db = MagicMock()
    request = _make_request()

    with pytest.raises(HTTPException) as exc_info:
        await generate_feedback(db, user_id=1, essay_id=1, request=request)

    assert exc_info.value.status_code == 404
    assert "API key" in exc_info.value.detail


# ---------------------------------------------------------------------------
# generate_feedback happy path tests
# ---------------------------------------------------------------------------


_MOCK_CRITERIA = [
    CriterionResult(name="Task Response", score=7.0, feedback="Good"),
    CriterionResult(name="Coherence & Cohesion", score=6.5, feedback="Decent"),
    CriterionResult(name="Lexical Resource", score=7.0, feedback="Good vocab"),
    CriterionResult(name="Grammatical Range & Accuracy", score=6.0, feedback="OK"),
]

_MOCK_SCORING_RESULT = ScoringResult(
    overall_score=6.5,
    overall_feedback="Solid essay overall.",
    criteria=_MOCK_CRITERIA,
)


@patch(
    "app.services.feedback_service.user_api_key_crud.update_last_used",
    new_callable=AsyncMock,
)
@patch(
    "app.services.feedback_service.feedback_crud.create_feedback",
    new_callable=AsyncMock,
)
@patch(
    "app.services.feedback_service.api_model_crud.get_api_model_by_name_and_provider",
    new_callable=AsyncMock,
    return_value=MagicMock(bot=MagicMock(id=5)),
)
@patch("app.services.feedback_service.Aggregator")
@patch(
    "app.services.feedback_service.generate_aggregator_agent", return_value=MagicMock()
)
@patch("app.services.feedback_service.ScoringSwarm")
@patch("app.services.feedback_service.generate_criterion_agents", return_value=[])
@patch("app.services.feedback_service.load_rubric", return_value=MagicMock())
@patch("app.services.feedback_service.get_llm_client", return_value=MagicMock())
@patch(
    "app.services.feedback_service.user_api_key_crud.get_user_api_key",
    new_callable=AsyncMock,
)
@patch(
    "app.services.feedback_service.ai_provider_crud.get_provider_by_name",
    new_callable=AsyncMock,
    return_value=MagicMock(id=1),
)
@patch(
    "app.services.feedback_service.essay_crud.get_essay_by_id",
    new_callable=AsyncMock,
    return_value=MagicMock(content="My essay about climate change", prompt_id=10),
)
async def test_generate_feedback_happy_path(
    mock_get_essay,
    mock_get_provider,
    mock_get_api_key,
    mock_get_llm,
    mock_load_rubric,
    mock_gen_agents,
    mock_swarm_cls,
    mock_gen_agg_agent,
    mock_agg_cls,
    mock_get_api_model,
    mock_create_feedback,
    mock_update_last_used,
):
    """generate_feedback should orchestrate swarm scoring and store feedback."""
    mock_get_api_key.return_value = _make_mock_api_key()

    # Configure ScoringSwarm mock
    mock_swarm = MagicMock()
    mock_swarm.score = AsyncMock(return_value=_MOCK_CRITERIA)
    mock_swarm_cls.return_value = mock_swarm

    # Configure Aggregator mock
    mock_agg = MagicMock()
    mock_agg.aggregate = AsyncMock(return_value=_MOCK_SCORING_RESULT)
    mock_agg_cls.return_value = mock_agg

    db = MagicMock()
    request = _make_request()

    await generate_feedback(db, user_id=1, essay_id=1, request=request)

    # Swarm was used
    mock_swarm.add_agents.assert_called_once()
    mock_swarm.score.assert_called_once()

    # Aggregator was used
    mock_agg.aggregate.assert_called_once()

    # Feedback stored in DB
    mock_create_feedback.assert_called_once()
    created = (
        mock_create_feedback.call_args[1].get("feedback_create")
        or mock_create_feedback.call_args[0][1]
    )
    assert created.content["overall_score"] == 6.5
    assert "Task Response" in created.content["feedback_by_criteria"]

    # Last used updated
    mock_update_last_used.assert_called_once()


@patch(
    "app.services.feedback_service.user_api_key_crud.update_last_used",
    new_callable=AsyncMock,
)
@patch(
    "app.services.feedback_service.feedback_crud.create_feedback",
    new_callable=AsyncMock,
)
@patch(
    "app.services.feedback_service.api_model_crud.get_api_model_by_name_and_provider",
    new_callable=AsyncMock,
    return_value=MagicMock(bot=MagicMock(id=5)),
)
@patch("app.services.feedback_service.Aggregator")
@patch(
    "app.services.feedback_service.generate_aggregator_agent", return_value=MagicMock()
)
@patch("app.services.feedback_service.ScoringSwarm")
@patch("app.services.feedback_service.generate_criterion_agents", return_value=[])
@patch("app.services.feedback_service.load_rubric", return_value=MagicMock())
@patch("app.services.feedback_service.get_llm_client", return_value=MagicMock())
@patch(
    "app.services.feedback_service.user_api_key_crud.get_user_api_key",
    new_callable=AsyncMock,
)
@patch(
    "app.services.feedback_service.ai_provider_crud.get_provider_by_name",
    new_callable=AsyncMock,
    return_value=MagicMock(id=1),
)
@patch(
    "app.services.feedback_service.essay_crud.get_essay_by_id",
    new_callable=AsyncMock,
    return_value=MagicMock(content="Original essay text", prompt_id=10),
)
async def test_generate_feedback_uses_override_content(
    mock_get_essay,
    mock_get_provider,
    mock_get_api_key,
    mock_get_llm,
    mock_load_rubric,
    mock_gen_agents,
    mock_swarm_cls,
    mock_gen_agg_agent,
    mock_agg_cls,
    mock_get_api_model,
    mock_create_feedback,
    mock_update_last_used,
):
    """When override_content is provided, swarm should score that text instead of essay.content."""
    mock_get_api_key.return_value = _make_mock_api_key()

    mock_swarm = MagicMock()
    mock_swarm.score = AsyncMock(return_value=_MOCK_CRITERIA)
    mock_swarm_cls.return_value = mock_swarm

    mock_agg = MagicMock()
    mock_agg.aggregate = AsyncMock(return_value=_MOCK_SCORING_RESULT)
    mock_agg_cls.return_value = mock_agg

    db = MagicMock()
    request = _make_request()

    await generate_feedback(
        db,
        user_id=1,
        essay_id=1,
        request=request,
        override_content="OCR extracted text",
    )

    # Verify swarm received the override text, not the original essay content
    score_call = mock_swarm.score.call_args
    assert score_call.kwargs.get("student_essay") == "OCR extracted text"


# ---------------------------------------------------------------------------
# generate_feedback_for_handwriting tests
# ---------------------------------------------------------------------------


@patch(
    "app.services.feedback_service.essay_crud.get_essay_by_id",
    new_callable=AsyncMock,
    return_value=MagicMock(image_path=None),
)
async def test_handwriting_no_image_raises_400(mock_get_essay):
    """generate_feedback_for_handwriting should raise 400 when no image is present."""
    db = MagicMock()
    request = _make_request()

    with pytest.raises(HTTPException) as exc_info:
        await generate_feedback_for_handwriting(
            db, user_id=1, essay_id=1, request=request
        )

    assert exc_info.value.status_code == 400
    assert "No image" in exc_info.value.detail


@patch(
    "app.services.feedback_service.ai_provider_crud.get_provider_by_name",
    new_callable=AsyncMock,
    return_value=None,
)
@patch(
    "app.services.feedback_service.asyncio.to_thread",
    new_callable=AsyncMock,
    return_value=b"fake_image_bytes",
)
@patch(
    "app.services.feedback_service.essay_crud.get_essay_by_id",
    new_callable=AsyncMock,
    return_value=MagicMock(image_path="/fake/path.png"),
)
async def test_handwriting_missing_provider_raises_404(
    mock_get_essay, mock_to_thread, mock_get_provider
):
    """generate_feedback_for_handwriting should raise 404 for unknown provider."""
    db = MagicMock()
    request = _make_request(provider="UnknownProvider")

    with pytest.raises(HTTPException) as exc_info:
        await generate_feedback_for_handwriting(
            db, user_id=1, essay_id=1, request=request
        )

    assert exc_info.value.status_code == 404
    assert "UnknownProvider" in exc_info.value.detail


@patch(
    "app.services.feedback_service.user_api_key_crud.get_user_api_key",
    new_callable=AsyncMock,
    return_value=None,
)
@patch(
    "app.services.feedback_service.ai_provider_crud.get_provider_by_name",
    new_callable=AsyncMock,
    return_value=MagicMock(id=1),
)
@patch(
    "app.services.feedback_service.asyncio.to_thread",
    new_callable=AsyncMock,
    return_value=b"fake_image_bytes",
)
@patch(
    "app.services.feedback_service.essay_crud.get_essay_by_id",
    new_callable=AsyncMock,
    return_value=MagicMock(image_path="/fake/path.png"),
)
async def test_handwriting_missing_api_key_raises_404(
    mock_get_essay, mock_to_thread, mock_get_provider, mock_get_api_key
):
    """generate_feedback_for_handwriting should raise 404 when user has no API key."""
    db = MagicMock()
    request = _make_request()

    with pytest.raises(HTTPException) as exc_info:
        await generate_feedback_for_handwriting(
            db, user_id=1, essay_id=1, request=request
        )

    assert exc_info.value.status_code == 404
    assert "API key" in exc_info.value.detail


@patch(
    "app.services.feedback_service.generate_feedback",
    new_callable=AsyncMock,
)
@patch(
    "app.services.feedback_service.essay_crud.update_ocr_text",
    new_callable=AsyncMock,
)
@patch("app.services.feedback_service.get_vlm_client")
@patch(
    "app.services.feedback_service.user_api_key_crud.get_user_api_key",
    new_callable=AsyncMock,
)
@patch(
    "app.services.feedback_service.ai_provider_crud.get_provider_by_name",
    new_callable=AsyncMock,
    return_value=MagicMock(id=1),
)
@patch(
    "app.services.feedback_service.asyncio.to_thread",
    new_callable=AsyncMock,
    return_value=b"fake_image_bytes",
)
@patch(
    "app.services.feedback_service.essay_crud.get_essay_by_id",
    new_callable=AsyncMock,
    return_value=MagicMock(image_path="/fake/path.png"),
)
async def test_handwriting_happy_path(
    mock_get_essay,
    mock_to_thread,
    mock_get_provider,
    mock_get_api_key,
    mock_get_vlm,
    mock_update_ocr,
    mock_gen_feedback,
):
    """generate_feedback_for_handwriting should OCR image and delegate to generate_feedback."""
    mock_get_api_key.return_value = _make_mock_api_key()

    # VLM returns extracted text
    mock_vlm = MagicMock()
    mock_vlm.ainvoke = AsyncMock(return_value=MagicMock(content="Extracted essay text"))
    mock_get_vlm.return_value = mock_vlm

    db = MagicMock()
    request = _make_request()

    await generate_feedback_for_handwriting(db, user_id=1, essay_id=1, request=request)

    # OCR text stored
    mock_update_ocr.assert_called_once_with(db, 1, "Extracted essay text")

    # Delegated to generate_feedback with override_content
    mock_gen_feedback.assert_called_once_with(
        db, 1, 1, request, override_content="Extracted essay text"
    )
