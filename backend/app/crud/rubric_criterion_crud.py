from sqlalchemy import and_, desc, distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RubricCriterion, Rubric
from app.schemas import rubric_criterion_schema


async def create_rubric_criterion(
    db: AsyncSession,
    rubric_create_criterion: rubric_criterion_schema.RubricCriterionCreate,
) -> rubric_criterion_schema.RubricCriterion:
    db_rubric_criterion = RubricCriterion(
        rubric_id=rubric_create_criterion.rubric_id,
        name=rubric_create_criterion.name,
        description=rubric_create_criterion.description,
        score=rubric_create_criterion.score,
    )
    db.add(db_rubric_criterion)
    await db.commit()
    return db_rubric_criterion


async def get_criterion_by_name_and_score(
    db: AsyncSession, name: str, score: int
) -> rubric_criterion_schema.RubricCriterion:
    result = await db.execute(
        select(RubricCriterion).where(
            and_(RubricCriterion.name == name.strip(), RubricCriterion.score == score)
        )
    )
    return result.scalars().first()


async def get_criterion_by_name(
    db: AsyncSession, criteria_name: str
) -> list[rubric_criterion_schema.RubricCriterion]:
    result = await db.execute(
        select(RubricCriterion)
        .where(RubricCriterion.name == criteria_name.strip())
        .order_by(desc(RubricCriterion.score))
    )
    return result.scalars().all()


async def get_unique_criterion_names_by_rubric(
    db: AsyncSession, rubric_name: str
) -> list[str]:
    result = await db.execute(
        select(distinct(RubricCriterion.name))
        .join(Rubric)
        .where(Rubric.name == rubric_name)
    )

    return [name for (name,) in result.all()]
