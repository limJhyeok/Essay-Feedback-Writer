from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Rubric
from app.schemas import rubric_schema


async def create_rubric(
    db: AsyncSession, rubric_create: rubric_schema.RubricCreate
) -> rubric_schema.Rubric:
    db_rubric = Rubric(
        name=rubric_create.name,
        subject=rubric_create.subject,
        language=rubric_create.language,
        description=rubric_create.description,
        scoring_method=rubric_create.scoring_method,
        weights=rubric_create.weights,
        created_by=rubric_create.created_by,
    )
    db.add(db_rubric)
    await db.commit()
    return db_rubric


async def get_rubric_by_name(db: AsyncSession, name: str) -> rubric_schema.Rubric:
    result = await db.execute(
        select(Rubric)
        .options(selectinload(Rubric.criteria))
        .where(Rubric.name == name.strip())
    )
    return result.scalars().first()
