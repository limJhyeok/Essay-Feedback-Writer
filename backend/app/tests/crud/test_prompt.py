from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import prompt_crud
from app.models import User
from app.schemas import prompt_schema
from app.tests.utils.utils import random_lower_string


async def test_create_prompt(db: AsyncSession, test_user: User) -> None:
    content = f"Prompt create test {random_lower_string()[:10]}"
    prompt_create = prompt_schema.PromptCreate(
        content=content,
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    result = await prompt_crud.create_prompt(db, prompt_create)

    assert result is not None
    assert result.id is not None
    assert result.content == content
    assert result.created_by == test_user.id


async def test_get_prompt_by_id(db: AsyncSession, test_user: User) -> None:
    content = f"Prompt get_by_id test {random_lower_string()[:10]}"
    prompt_create = prompt_schema.PromptCreate(
        content=content,
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    created = await prompt_crud.create_prompt(db, prompt_create)

    fetched = await prompt_crud.get_prompt_by_id(db, created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.content == created.content


async def test_get_prompt_by_content(db: AsyncSession, test_user: User) -> None:
    content = f"Prompt get_by_content test {random_lower_string()[:10]}"
    prompt_create = prompt_schema.PromptCreate(
        content=content,
        created_by=test_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    created = await prompt_crud.create_prompt(db, prompt_create)

    fetched = await prompt_crud.get_prompt_by_content(db, content)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.content == content
