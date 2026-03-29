from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import DomainType, Prompt
from app.schemas import prompt_schema


async def create_prompt(
    db: AsyncSession, prompt_create: prompt_schema.PromptCreate
) -> Prompt:
    db_prompt = Prompt(
        content=prompt_create.content,
        created_by=prompt_create.created_by,
        created_at=prompt_create.created_at,
        updated_at=prompt_create.updated_at,
    )
    db.add(db_prompt)
    await db.commit()
    return db_prompt


async def get_prompts(
    db: AsyncSession, domain: DomainType | None = None
) -> list[Prompt]:
    stmt = select(Prompt).options(selectinload(Prompt.reactions))
    if domain is not None:
        stmt = stmt.where(Prompt.domain == domain)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_prompt_by_content(db: AsyncSession, content: str) -> Prompt:
    result = await db.execute(select(Prompt).where(Prompt.content == content.strip()))
    return result.scalars().first()


async def get_prompt_by_id(db: AsyncSession, prompt_id: int) -> Prompt | None:
    result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
    return result.scalars().first()
