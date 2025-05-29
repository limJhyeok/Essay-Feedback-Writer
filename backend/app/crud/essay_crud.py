import re
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.models import Essay
from app.schemas import essay_schema


def normalise_content(content: str) -> str:
    return re.sub(r"\s+", " ", content.strip())


def create_essay(
    db: Session, essay_create: essay_schema.EssayCreate
) -> essay_schema.Essay:
    db_essay = Essay(
        user_id=essay_create.user_id,
        prompt_id=essay_create.prompt_id,
        content=essay_create.content,
        submitted_at=essay_create.submitted_at,
    )
    db.add(db_essay)
    db.commit()
    db.refresh(db_essay)

    return essay_schema.Essay.from_orm(db_essay)


def get_essay_by_id(db: Session, id: int) -> essay_schema.Essay:
    essay = db.query(Essay).filter(Essay.id == id).first()
    return essay


def get_duplicated_essay(
    db: Session, user_id: int, prompt_id: int, content: str
) -> essay_schema.Essay | None:
    db_essays = (
        db.query(Essay)
        .filter(
            and_(
                Essay.user_id == user_id,
                Essay.prompt_id == prompt_id,
            )
        )
        .all()
    )
    for db_essay in db_essays:
        if normalise_content(db_essay.content) == normalise_content(content):
            return db_essay


def get_essay_list_by_prompt_id(
    db: Session, user_id: int, prompt_id: int
) -> list[essay_schema.EssayPublic]:
    essay_list = (
        db.query(Essay)
        .filter(and_(Essay.user_id == user_id, Essay.prompt_id == prompt_id))
        .order_by(desc(Essay.submitted_at))
        .all()
    )
    return essay_list
