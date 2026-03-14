from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import prompt_crud
from app.models import ExampleEssay
from app.schemas import example_essay_schema


async def create_example_essay(
    db: AsyncSession, example_essay_create: example_essay_schema.ExampleEssayCreate
) -> ExampleEssay:
    db_example_essay = ExampleEssay(
        prompt_id=example_essay_create.prompt_id,
        content=example_essay_create.content,
        created_at=example_essay_create.created_at,
        updated_at=example_essay_create.updated_at,
    )
    db.add(db_example_essay)
    await db.commit()
    return db_example_essay


async def get_example_essay(db: AsyncSession, id: int) -> ExampleEssay:
    result = await db.execute(select(ExampleEssay).where(ExampleEssay.id == id))
    return result.scalars().first()


async def get_example_essay_by_content(db: AsyncSession, content: str) -> ExampleEssay:
    result = await db.execute(
        select(ExampleEssay).where(ExampleEssay.content == content)
    )
    return result.scalars().first()


async def get_example_essay_by_prompt_id(
    db: AsyncSession, prompt_id: int
) -> ExampleEssay:
    prompt = await prompt_crud.get_prompt_by_id(db, prompt_id)
    if prompt:
        result = await db.execute(
            select(ExampleEssay).where(ExampleEssay.prompt_id == prompt.id)
        )
        return result.scalars().first()
