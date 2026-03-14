from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Feedback
from app.schemas import feedback_schema


async def create_feedback(
    db: AsyncSession, feedback_create: feedback_schema.FeedbackCreate
) -> feedback_schema.Feedback:
    db_feedback = Feedback(
        user_id=feedback_create.user_id,
        prompt_id=feedback_create.prompt_id,
        essay_id=feedback_create.essay_id,
        bot_id=feedback_create.bot_id,
        content=feedback_create.content,
        created_at=feedback_create.created_at,
    )
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)

    return feedback_schema.Feedback.from_orm(db_feedback)


async def get_feedbacks_by_user_prompt_essay(
    db: AsyncSession, user_id: int, prompt_id: int, essay_id: int
) -> list[Feedback]:
    result = await db.execute(
        select(Feedback)
        .options(selectinload(Feedback.bot))
        .where(
            and_(
                Feedback.user_id == user_id,
                Feedback.prompt_id == prompt_id,
                Feedback.essay_id == essay_id,
            )
        )
        .order_by(desc(Feedback.created_at))
    )
    return result.scalars().all()
