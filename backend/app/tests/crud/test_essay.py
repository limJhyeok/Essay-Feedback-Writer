from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import essay_crud, prompt_crud
from app.models import Prompt, User
from app.schemas import essay_schema, prompt_schema


async def test_create_essay_and_get_by_id(
    db: AsyncSession, test_user: User, test_prompt: Prompt
) -> None:
    essay_create = essay_schema.EssayCreate(
        user_id=test_user.id,
        prompt_id=test_prompt.id,
        content="Technology has transformed the way students learn.",
        submitted_at=datetime.now(timezone.utc),
    )
    created = await essay_crud.create_essay(db, essay_create)

    assert created.id is not None
    assert created.user_id == test_user.id
    assert created.prompt_id == test_prompt.id
    assert created.content == essay_create.content

    fetched = await essay_crud.get_essay_by_id(db, created.id)

    assert fetched is not None
    assert fetched.id == created.id


async def test_get_duplicated_essay(
    db: AsyncSession, test_user: User, test_prompt: Prompt
) -> None:
    content = "This is a unique essay for duplication test."
    essay_create = essay_schema.EssayCreate(
        user_id=test_user.id,
        prompt_id=test_prompt.id,
        content=content,
        submitted_at=datetime.now(timezone.utc),
    )
    original = await essay_crud.create_essay(db, essay_create)

    # Same content with extra whitespace — should still match via normalise_content
    dup = await essay_crud.get_duplicated_essay(
        db, test_user.id, test_prompt.id, f"  {content}  "
    )

    assert dup is not None
    assert dup.id == original.id


async def test_get_essay_list_by_prompt_id(db: AsyncSession, test_user: User) -> None:
    # Create a dedicated prompt to isolate this test
    pc = prompt_schema.PromptCreate(
        content="Prompt for essay list test.",
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    prompt = await prompt_crud.create_prompt(db, pc)

    await essay_crud.create_essay(
        db,
        essay_schema.EssayCreate(
            user_id=test_user.id,
            prompt_id=prompt.id,
            content="First essay for list test.",
            submitted_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        ),
    )
    await essay_crud.create_essay(
        db,
        essay_schema.EssayCreate(
            user_id=test_user.id,
            prompt_id=prompt.id,
            content="Second essay for list test.",
            submitted_at=datetime(2025, 6, 1, tzinfo=timezone.utc),
        ),
    )

    result = await essay_crud.get_essay_list_by_prompt_id(db, test_user.id, prompt.id)

    assert len(result) >= 2
    # Verify descending order by submitted_at
    assert result[0].submitted_at >= result[1].submitted_at
