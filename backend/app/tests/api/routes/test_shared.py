from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


async def test_read_bots(client: AsyncClient, db: AsyncSession) -> None:
    r = await client.get(f"{settings.API_V1_STR}/shared/bots")

    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_read_providers(client: AsyncClient, db: AsyncSession) -> None:
    r = await client.get(f"{settings.API_V1_STR}/shared/providers")

    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_create_and_list_api_keys(
    client: AsyncClient,
    db: AsyncSession,
    normal_user_token_headers: dict[str, str],
    openai_provider,
) -> None:
    create_data = {
        "provider_name": "OpenAI",
        "name": "route-test-key",
        "api_key": "sk-route-test-123",
    }
    r_create = await client.post(
        f"{settings.API_V1_STR}/shared/api_keys",
        headers=normal_user_token_headers,
        json=create_data,
    )
    assert r_create.status_code == 204

    r_list = await client.get(
        f"{settings.API_V1_STR}/shared/api_keys",
        headers=normal_user_token_headers,
    )
    assert r_list.status_code == 200
    keys = r_list.json()
    assert isinstance(keys, list)
    assert len(keys) >= 1
    assert any(k["name"] == "route-test-key" for k in keys)


async def test_delete_api_key(
    client: AsyncClient,
    db: AsyncSession,
    normal_user_token_headers: dict[str, str],
    openai_provider,
) -> None:
    # Create a key to delete
    create_data = {
        "provider_name": "OpenAI",
        "name": "delete-route-key",
        "api_key": "sk-delete-test-456",
    }
    await client.post(
        f"{settings.API_V1_STR}/shared/api_keys",
        headers=normal_user_token_headers,
        json=create_data,
    )

    # Get the id
    r_list = await client.get(
        f"{settings.API_V1_STR}/shared/api_keys",
        headers=normal_user_token_headers,
    )
    key_id = next(k["id"] for k in r_list.json() if k["name"] == "delete-route-key")

    # Delete
    r_delete = await client.delete(
        f"{settings.API_V1_STR}/shared/api_keys/{key_id}",
    )
    assert r_delete.status_code == 200

    # Verify deleted
    r_list_after = await client.get(
        f"{settings.API_V1_STR}/shared/api_keys",
        headers=normal_user_token_headers,
    )
    assert all(k["id"] != key_id for k in r_list_after.json())
