from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_api_key_crud
from app.schemas import user_api_key_schema


async def test_create_and_get_user_api_key(
    db: AsyncSession, superuser, openai_provider, cleanup_api_keys
) -> None:
    key_create = user_api_key_schema.UserAPIKeyCreate(
        user_id=superuser.id,
        provider_id=openai_provider.id,
        name="test-key-1",
        api_key="sk-test-encrypted-value-123",
    )
    created = await user_api_key_crud.create_user_api_key(db, key_create)

    assert created.id is not None
    assert created.user_id == superuser.id
    assert created.name == "test-key-1"
    assert created.is_active is True

    fetched = await user_api_key_crud.get_user_api_key(
        db, superuser.id, openai_provider.id
    )

    assert fetched is not None
    assert fetched.id == created.id


async def test_get_user_api_key_list(
    db: AsyncSession, superuser, openai_provider, cleanup_api_keys
) -> None:
    key_create = user_api_key_schema.UserAPIKeyCreate(
        user_id=superuser.id,
        provider_id=openai_provider.id,
        name="list-test-key",
        api_key="sk-test-list-value",
    )
    await user_api_key_crud.create_user_api_key(db, key_create)

    result = await user_api_key_crud.get_user_api_key_list(db, superuser.id)

    assert isinstance(result, list)
    assert len(result) >= 1
    # Verify provider is eagerly loaded via selectinload
    assert result[0].provider is not None


async def test_delete_api_key(
    db: AsyncSession, superuser, openai_provider, cleanup_api_keys
) -> None:
    key_create = user_api_key_schema.UserAPIKeyCreate(
        user_id=superuser.id,
        provider_id=openai_provider.id,
        name="delete-test-key",
        api_key="sk-test-delete-value",
    )
    created = await user_api_key_crud.create_user_api_key(db, key_create)

    await user_api_key_crud.delete_api_key(db, created.id)

    remaining = await user_api_key_crud.get_user_api_key_list(db, superuser.id)
    assert all(k.id != created.id for k in remaining)
