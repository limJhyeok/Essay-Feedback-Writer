from datetime import datetime, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud import prompt_crud
from app.schemas import prompt_schema


async def test_list_exams(client: AsyncClient, db: AsyncSession) -> None:
    r = await client.get(f"{settings.API_V1_STR}/ksat/exams")

    assert r.status_code == 200
    assert isinstance(r.json(), list)
    # Verify exam_type field is present in response if exams exist
    if r.json():
        assert "exam_type" in r.json()[0]


async def test_get_exam_not_found(client: AsyncClient, db: AsyncSession) -> None:
    r = await client.get(f"{settings.API_V1_STR}/ksat/exams/999999")

    assert r.status_code == 404
    assert r.json()["detail"] == "Exam not found"


async def test_submit_and_list_ksat_essays(
    client: AsyncClient,
    db: AsyncSession,
    normal_user_token_headers: dict[str, str],
    test_user,
) -> None:
    # Create a prompt for this test
    ksat_prompt = await prompt_crud.create_prompt(
        db,
        prompt_schema.PromptCreate(
            content="KSAT route test prompt.",
            created_by=test_user.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    )

    # Submit essay
    submit_data = {
        "prompt_id": ksat_prompt.id,
        "content": "KSAT test essay content for route validation.",
    }
    r_submit = await client.post(
        f"{settings.API_V1_STR}/ksat/essays",
        headers=normal_user_token_headers,
        json=submit_data,
    )
    assert r_submit.status_code == 200
    assert "id" in r_submit.json()

    # List essays
    r_list = await client.get(
        f"{settings.API_V1_STR}/ksat/essays",
        headers=normal_user_token_headers,
        params={"prompt_id": ksat_prompt.id},
    )
    assert r_list.status_code == 200
    assert len(r_list.json()) >= 1
