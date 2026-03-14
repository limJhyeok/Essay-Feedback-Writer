import re
from sqlalchemy import and_, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Essay, InputType
from app.schemas import essay_schema


def normalise_content(content: str) -> str:
    return re.sub(r"\s+", " ", content.strip())


async def create_essay(
    db: AsyncSession, essay_create: essay_schema.EssayCreate
) -> essay_schema.Essay:
    db_essay = Essay(
        user_id=essay_create.user_id,
        prompt_id=essay_create.prompt_id,
        content=essay_create.content,
        submitted_at=essay_create.submitted_at,
    )
    db.add(db_essay)
    await db.commit()
    await db.refresh(db_essay)

    return essay_schema.Essay.from_orm(db_essay)


async def get_essay_by_id(db: AsyncSession, id: int) -> essay_schema.Essay:
    result = await db.execute(select(Essay).where(Essay.id == id))
    return result.scalars().first()


async def get_duplicated_essay(
    db: AsyncSession, user_id: int, prompt_id: int, content: str
) -> essay_schema.Essay | None:
    result = await db.execute(
        select(Essay).where(
            and_(
                Essay.user_id == user_id,
                Essay.prompt_id == prompt_id,
            )
        )
    )
    db_essays = result.scalars().all()
    for db_essay in db_essays:
        if normalise_content(db_essay.content) == normalise_content(content):
            return db_essay


async def create_handwriting_essay(
    db: AsyncSession, user_id: int, prompt_id: int, submitted_at
) -> Essay:
    db_essay = Essay(
        user_id=user_id,
        prompt_id=prompt_id,
        input_type=InputType.handwriting,
        submitted_at=submitted_at,
    )
    db.add(db_essay)
    await db.commit()
    await db.refresh(db_essay)
    return db_essay


async def update_essay_image_path(
    db: AsyncSession, essay_id: int, image_path: str
) -> None:
    await db.execute(
        update(Essay).where(Essay.id == essay_id).values(image_path=image_path)
    )
    await db.commit()


async def update_ocr_text(db: AsyncSession, essay_id: int, ocr_text: str) -> None:
    await db.execute(
        update(Essay).where(Essay.id == essay_id).values(ocr_text=ocr_text)
    )
    await db.commit()


async def get_essay_list_by_prompt_id(
    db: AsyncSession, user_id: int, prompt_id: int
) -> list[essay_schema.EssayPublic]:
    result = await db.execute(
        select(Essay)
        .where(and_(Essay.user_id == user_id, Essay.prompt_id == prompt_id))
        .order_by(desc(Essay.submitted_at))
    )
    return result.scalars().all()
