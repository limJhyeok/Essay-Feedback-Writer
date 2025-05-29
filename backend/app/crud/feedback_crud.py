from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.models import Feedback
from app.schemas import feedback_schema


def create_feedback(
    db: Session, feedback_create: feedback_schema.FeedbackCreate
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
    db.commit()
    db.refresh(db_feedback)

    return feedback_schema.Feedback.from_orm(db_feedback)


def get_feedbacks_by_user_prompt_essay(
    db: Session, user_id: int, prompt_id: int, essay_id: int
) -> list[Feedback]:
    db_feedback_list = (
        db.query(Feedback)
        .filter(
            and_(
                Feedback.user_id == user_id,
                Feedback.prompt_id == prompt_id,
                Feedback.essay_id == essay_id,
            )
        )
        .order_by(desc(Feedback.created_at))
        .all()
    )
    return db_feedback_list
