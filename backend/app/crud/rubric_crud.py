from sqlalchemy.orm import Session

from app.models import Rubric
from app.schemas import rubric_schema


def create_rubric(
    db: Session, rubric_create: rubric_schema.RubricCreate
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
    db.commit()
    return db_rubric


def get_rubric_by_name(db: Session, name: str) -> rubric_schema.Rubric:
    rubric = db.query(Rubric).filter(Rubric.name == name.strip()).first()
    return rubric
