from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, distinct

from app.models import RubricCriterion, Rubric
from app.schemas import rubric_criterion_schema


def create_rubric_criterion(
    db: Session, rubric_create_criterion: rubric_criterion_schema.RubricCriterionCreate
) -> rubric_criterion_schema.RubricCriterion:
    db_rubric_criterion = RubricCriterion(
        rubric_id=rubric_create_criterion.rubric_id,
        name=rubric_create_criterion.name,
        description=rubric_create_criterion.description,
        score=rubric_create_criterion.score,
    )
    db.add(db_rubric_criterion)
    db.commit()
    return db_rubric_criterion


def get_criterion_by_name_and_score(
    db: Session, name: str, score: int
) -> rubric_criterion_schema.RubricCriterion:
    rubric_criterion = (
        db.query(RubricCriterion)
        .filter(
            and_(RubricCriterion.name == name.strip(), RubricCriterion.score == score)
        )
        .first()
    )
    return rubric_criterion


def get_criterion_by_name(
    db: Session, criteria_name: str
) -> list[rubric_criterion_schema.RubricCriterion]:
    rubric_criteria = (
        db.query(RubricCriterion)
        .filter(RubricCriterion.name == criteria_name.strip())
        .order_by(desc(RubricCriterion.score))
        .all()
    )
    return rubric_criteria


def get_unique_criterion_names_by_rubric(db: Session, rubric_name: str) -> list[str]:
    names = (
        db.query(distinct(RubricCriterion.name))
        .join(Rubric)
        .filter(Rubric.name == rubric_name)
        .all()
    )

    return [name[0] for name in names]
