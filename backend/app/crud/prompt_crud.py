from sqlalchemy.orm import Session

from app.models import Prompt
from app.schemas import prompt_schema


def create_prompt(db: Session, prompt_create: prompt_schema.PromptCreate) -> Prompt:
    db_prompt = Prompt(
        content=prompt_create.content,
        created_by=prompt_create.created_by,
        created_at=prompt_create.created_at,
        updated_at=prompt_create.updated_at,
    )
    db.add(db_prompt)
    db.commit()
    return db_prompt


def get_prompts(db: Session) -> list[Prompt]:
    prompts = db.query(Prompt).all()
    return prompts


def get_prompt_by_content(db: Session, content: str) -> Prompt:
    prompt = db.query(Prompt).filter(Prompt.content == content.strip()).first()
    return prompt


def get_prompt_by_id(db: Session, prompt_id: int) -> Prompt | None:
    return db.query(Prompt).filter(Prompt.id == prompt_id).first()
