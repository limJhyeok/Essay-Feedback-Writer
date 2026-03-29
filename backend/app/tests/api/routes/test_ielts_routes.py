from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Prompt


async def test_get_prompts(client: AsyncClient, db: AsyncSession) -> None:
    r = await client.get(f"{settings.API_V1_STR}/ielts/prompts")

    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_submit_and_list_essays(
    client: AsyncClient,
    db: AsyncSession,
    normal_user_token_headers: dict[str, str],
    test_prompt: Prompt,
) -> None:
    submit_data = {
        "prompt_id": test_prompt.id,
        "content": "Route test essay: Technology changes education fundamentally.",
    }
    r_submit = await client.post(
        f"{settings.API_V1_STR}/ielts/essays",
        headers=normal_user_token_headers,
        json=submit_data,
    )
    assert r_submit.status_code == 200
    assert "id" in r_submit.json()
    assert "content" in r_submit.json()

    r_list = await client.get(
        f"{settings.API_V1_STR}/ielts/essays",
        headers=normal_user_token_headers,
        params={"prompt_id": test_prompt.id},
    )
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 1


async def test_get_feedbacks_empty(
    client: AsyncClient,
    db: AsyncSession,
    normal_user_token_headers: dict[str, str],
    test_prompt: Prompt,
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/ielts/feedbacks",
        headers=normal_user_token_headers,
        params={"prompt_id": test_prompt.id, "essay_id": 999999},
    )
    assert r.status_code == 200
    assert r.json() == []
