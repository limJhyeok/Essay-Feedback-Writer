from sqlalchemy.orm import Session

from app.crud import prompt_crud
from app.models import ExampleEssay
from app.schemas import example_essay_schema


def create_example_essay(
    db: Session, example_essay_create: example_essay_schema.ExampleEssayCreate
) -> ExampleEssay:
    db_example_essay = ExampleEssay(
        prompt_id=example_essay_create.prompt_id,
        content=example_essay_create.content,
        created_at=example_essay_create.created_at,
        updated_at=example_essay_create.updated_at,
    )
    db.add(db_example_essay)
    db.commit()
    return db_example_essay


def get_example_essay(db: Session, id: int) -> ExampleEssay:
    example_essay = db.query(ExampleEssay).filter(ExampleEssay.id == id).first()
    return example_essay


def get_example_essay_by_content(db: Session, content: str) -> ExampleEssay:
    example_essay = (
        db.query(ExampleEssay).filter(ExampleEssay.content == content).first()
    )
    return example_essay


def get_example_essay_by_prompt_id(db: Session, prompt_id: int) -> ExampleEssay:
    prompt = prompt_crud.get_prompt_by_id(db, prompt_id)
    if prompt:
        example_essay = (
            db.query(ExampleEssay).filter(ExampleEssay.prompt_id == prompt.id).first()
        )
        return example_essay
