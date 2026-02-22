from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.routes.ielts_router import FeedbackResponse, get_llm_client


def _make_mock_api_key():
    """Create a mock UserAPIKey DB object."""
    mock = MagicMock()
    mock.api_key = "encrypted_fake_key"
    mock.id = 1
    return mock


def test_get_llm_client_unsupported_provider_raises_400():
    """get_llm_client with unknown provider should raise HTTP 400."""
    db = MagicMock()
    mock_api_key = _make_mock_api_key()

    with pytest.raises(HTTPException) as exc_info:
        get_llm_client(db, mock_api_key, "NonExistentProvider", "some-model")

    assert exc_info.value.status_code == 400
    assert "Unsupported provider" in exc_info.value.detail


@patch("app.api.routes.ielts_router.security.decrypt_api_key", return_value="sk-fake")
def test_get_llm_client_openai_creates_chat_openai(mock_decrypt):
    """'OpenAI' provider should instantiate ChatOpenAI with correct params."""
    db = MagicMock()
    mock_api_key = _make_mock_api_key()
    mock_cls = MagicMock()
    mock_llm = MagicMock()
    mock_cls.return_value = mock_llm

    with patch.dict("app.api.routes.ielts_router._PROVIDER_MAP", {"OpenAI": mock_cls}):
        get_llm_client(db, mock_api_key, "OpenAI", "gpt-4o")

    mock_decrypt.assert_called_once_with("encrypted_fake_key")
    mock_cls.assert_called_once_with(model="gpt-4o", api_key="sk-fake")


@patch("app.api.routes.ielts_router.security.decrypt_api_key", return_value="sk-fake")
def test_get_llm_client_anthropic_creates_chat_anthropic(mock_decrypt):
    """'Anthropic' provider should instantiate ChatAnthropic with correct params."""
    db = MagicMock()
    mock_api_key = _make_mock_api_key()
    mock_cls = MagicMock()
    mock_llm = MagicMock()
    mock_cls.return_value = mock_llm

    with patch.dict(
        "app.api.routes.ielts_router._PROVIDER_MAP", {"Anthropic": mock_cls}
    ):
        get_llm_client(db, mock_api_key, "Anthropic", "claude-sonnet-4-5")

    mock_decrypt.assert_called_once_with("encrypted_fake_key")
    mock_cls.assert_called_once_with(model="claude-sonnet-4-5", api_key="sk-fake")


@patch("app.api.routes.ielts_router.security.decrypt_api_key", return_value="sk-fake")
def test_get_llm_client_returns_structured_output(mock_decrypt):
    """get_llm_client should return llm.with_structured_output(FeedbackResponse)."""
    db = MagicMock()
    mock_api_key = _make_mock_api_key()
    mock_cls = MagicMock()
    mock_llm = MagicMock()
    mock_cls.return_value = mock_llm
    mock_structured = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured

    with patch.dict("app.api.routes.ielts_router._PROVIDER_MAP", {"OpenAI": mock_cls}):
        result = get_llm_client(db, mock_api_key, "OpenAI", "gpt-4o")

    mock_llm.with_structured_output.assert_called_once_with(FeedbackResponse)
    assert result is mock_structured
