from datetime import datetime, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud import prompt_crud
from app.models import (
    DomainType,
    Exam,
    ExamQuestion,
    ExamType,
    TrackType,
)
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


async def test_exam_question_content_round_trips(
    client: AsyncClient,
    db: AsyncSession,
    test_user,
) -> None:
    """Question-owned passage content must round-trip through the API."""
    passage_text = "제시문 (가) 테스트 지문.\n\n제시문 (나) 또 다른 지문."

    prompt = await prompt_crud.create_prompt(
        db,
        prompt_schema.PromptCreate(
            content="지시문 테스트",
            created_by=test_user.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    )

    exam = Exam(
        domain=DomainType.ksat,
        university="테스트대학교",
        year=2099,
        track=TrackType.humanities,
        exam_type=ExamType.mock,
        content=None,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)

    question = ExamQuestion(
        exam_id=exam.id,
        prompt_id=prompt.id,
        question_number=1,
        max_points=40,
        char_min=500,
        char_max=600,
        passage_refs=["가", "나"],
        content=passage_text,
    )
    db.add(question)
    await db.commit()

    r_questions = await client.get(
        f"{settings.API_V1_STR}/ksat/exams/{exam.id}/questions"
    )
    assert r_questions.status_code == 200
    payload = r_questions.json()
    assert len(payload) == 1
    assert payload[0]["content"] == passage_text
    assert payload[0]["passage_refs"] == ["가", "나"]

    r_detail = await client.get(f"{settings.API_V1_STR}/ksat/exams/{exam.id}")
    assert r_detail.status_code == 200
    questions = r_detail.json()["questions"]
    assert len(questions) == 1
    assert questions[0]["content"] == passage_text

    await db.delete(question)
    await db.commit()
    await db.delete(exam)
    await db.commit()


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
