import os
from unittest.mock import patch

from app.core.db import store_default_api_key
from app.core.security import decrypt_api_key
from app.crud import user_api_key_crud


def test_store_both_api_keys(
    db, superuser, openai_provider, anthropic_provider, cleanup_api_keys
):
    """Both OPENAI_API_KEY and ANTHROPIC_API_KEY set → both keys stored."""
    env = {"OPENAI_API_KEY": "sk-openai-test", "ANTHROPIC_API_KEY": "sk-ant-test"}
    with patch.dict(os.environ, env, clear=False):
        store_default_api_key(db)

    openai_key = user_api_key_crud.get_user_api_key(
        db, superuser.id, provider_id=openai_provider.id
    )
    anthropic_key = user_api_key_crud.get_user_api_key(
        db, superuser.id, provider_id=anthropic_provider.id
    )

    assert openai_key is not None
    assert decrypt_api_key(openai_key.api_key) == "sk-openai-test"

    assert anthropic_key is not None
    assert decrypt_api_key(anthropic_key.api_key) == "sk-ant-test"


def test_store_only_openai_key(
    db, superuser, openai_provider, anthropic_provider, cleanup_api_keys
):
    """Only OPENAI_API_KEY set → only OpenAI key stored."""
    env = {"OPENAI_API_KEY": "sk-openai-only"}
    with patch.dict(os.environ, env, clear=False):
        # Remove ANTHROPIC_API_KEY if it happens to exist
        os.environ.pop("ANTHROPIC_API_KEY", None)
        store_default_api_key(db)

    openai_key = user_api_key_crud.get_user_api_key(
        db, superuser.id, provider_id=openai_provider.id
    )
    anthropic_key = user_api_key_crud.get_user_api_key(
        db, superuser.id, provider_id=anthropic_provider.id
    )

    assert openai_key is not None
    assert decrypt_api_key(openai_key.api_key) == "sk-openai-only"
    assert anthropic_key is None


def test_store_only_anthropic_key(
    db, superuser, openai_provider, anthropic_provider, cleanup_api_keys
):
    """Only ANTHROPIC_API_KEY set → only Anthropic key stored."""
    env = {"ANTHROPIC_API_KEY": "sk-ant-only"}
    with patch.dict(os.environ, env, clear=False):
        os.environ.pop("OPENAI_API_KEY", None)
        store_default_api_key(db)

    openai_key = user_api_key_crud.get_user_api_key(
        db, superuser.id, provider_id=openai_provider.id
    )
    anthropic_key = user_api_key_crud.get_user_api_key(
        db, superuser.id, provider_id=anthropic_provider.id
    )

    assert openai_key is None
    assert anthropic_key is not None
    assert decrypt_api_key(anthropic_key.api_key) == "sk-ant-only"


def test_store_no_api_keys(
    db, superuser, openai_provider, anthropic_provider, cleanup_api_keys
):
    """Neither env var set → no keys created."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)
        store_default_api_key(db)

    openai_key = user_api_key_crud.get_user_api_key(
        db, superuser.id, provider_id=openai_provider.id
    )
    anthropic_key = user_api_key_crud.get_user_api_key(
        db, superuser.id, provider_id=anthropic_provider.id
    )

    assert openai_key is None
    assert anthropic_key is None


def test_store_api_key_idempotent(db, superuser, openai_provider, cleanup_api_keys):
    """Running twice with the same env → no duplicate key created."""
    env = {"OPENAI_API_KEY": "sk-openai-idem"}
    with patch.dict(os.environ, env, clear=False):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        store_default_api_key(db)
        store_default_api_key(db)

    keys = user_api_key_crud.get_user_api_key_list(db, superuser.id)
    openai_keys = [k for k in keys if k.provider_id == openai_provider.id]
    assert len(openai_keys) == 1
    assert decrypt_api_key(openai_keys[0].api_key) == "sk-openai-idem"


def test_store_api_key_skips_missing_provider(db, superuser, cleanup_api_keys):
    """Provider not in DB → gracefully skipped, no error."""
    # Use a provider name that doesn't exist in the DB.
    # We only need to ensure the env var is set but the provider is missing.
    env = {"OPENAI_API_KEY": "sk-openai-noprov", "ANTHROPIC_API_KEY": "sk-ant-noprov"}

    # Delete providers temporarily by patching get_provider_by_name to return None
    with patch.dict(os.environ, env, clear=False), patch(
        "app.core.db.ai_provider_crud.get_provider_by_name", return_value=None
    ):
        store_default_api_key(db)  # should not raise

    # No keys should have been created since providers were "missing"
    keys = user_api_key_crud.get_user_api_key_list(db, superuser.id)
    assert len(keys) == 0
