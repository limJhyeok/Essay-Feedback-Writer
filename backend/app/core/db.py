import logging

from sqlalchemy.orm import Session

import os
import csv
from typing import Any
from datetime import datetime

from sqlalchemy import create_engine
from app.core.config import settings

from app.core.security import encrypt_api_key

from app.schemas import (
    user_schema,
    example_essay_schema,
    rubric_schema,
    rubric_criterion_schema,
    prompt_schema,
    bot_schema,
    api_model_schema,
    ai_provider_schema,
    user_api_key_schema,
)
from app.crud import (
    user_crud,
    example_essay_crud,
    rubric_criterion_crud,
    rubric_crud,
    prompt_crud,
    bot_crud,
    api_model_crud,
    ai_provider_crud,
    user_api_key_crud,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
    if not user:
        user_create = user_schema.UserCreate(
            email=settings.FIRST_SUPERUSER,
            is_superuser=True,
            password=settings.FIRST_SUPERUSER_PASSWORD,
        )
        user_crud.create_user(db, user_create)


def load_from_csv(csv_path: str) -> list[dict[str, Any]]:
    data = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cleaned_row = {
                k: v.strip() if isinstance(v, str) else v for k, v in row.items()
            }
            data.append(cleaned_row)
    return data


def store_example_essays(db: Session, csv_path: str) -> None:
    data = load_from_csv(csv_path)
    super_user = user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
    for item in data:
        prompt_content = item["prompt"].strip()
        example_answer = item["example_answer"].strip()

        existing_prompt = prompt_crud.get_prompt_by_content(db, content=prompt_content)
        if not existing_prompt:
            prompt_create = prompt_schema.PromptCreate(
                content=prompt_content,
                created_by=super_user.id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db_prompt = prompt_crud.create_prompt(db, prompt_create)

            existing_example = example_essay_crud.get_example_essay_by_content(
                db, example_answer
            )
            if not existing_example:
                example_essay_create = example_essay_schema.ExampleEssayCreate(
                    prompt_id=db_prompt.id,
                    content=example_answer,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

                _ = example_essay_crud.create_example_essay(db, example_essay_create)


def store_default_rubric(
    db: Session, csv_path: str, rubric_create: rubric_schema.RubricCreate
) -> None:
    data = load_from_csv(csv_path)
    existing_rubric = rubric_crud.get_rubric_by_name(db, rubric_create.name)
    if not existing_rubric:
        super_user = user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
        rubric_create.created_by = super_user.id
        db_rubric = rubric_crud.create_rubric(db, rubric_create)

        for row in data:
            score = row.pop("score")
            try:
                score = int(score)
            except ValueError:
                logger.error(f"Invalid score value '{score}' encountered.")

            for _criterion_name, _description in row.items():
                existing_criterion = (
                    rubric_criterion_crud.get_criterion_by_name_and_score(
                        db=db, name=_criterion_name, score=score
                    )
                )
                if not existing_criterion:
                    criterion_create = rubric_criterion_schema.RubricCriterionCreate(
                        rubric_id=db_rubric.id,
                        name=_criterion_name,
                        description=_description,
                        score=score,
                    )
                    _ = rubric_criterion_crud.create_rubric_criterion(
                        db, criterion_create
                    )


def store_default_bots(db: Session, csv_path: str) -> None:
    data = load_from_csv(csv_path)
    for row in data:
        existing_bot = bot_crud.get_bot_by_name(db, row["name"].strip())
        if not existing_bot:
            bot_create = bot_schema.BotCreate(
                name=row["name"].strip(),
                version=row.get("version").strip(),
                description=row.get("description").strip(),
            )
            bot_crud.create_bot(db, bot_create)


def store_default_ai_providers(db: Session, csv_path: str) -> None:
    data = load_from_csv(csv_path)
    for row in data:
        existing_provider = ai_provider_crud.get_provider_by_name(
            db, provider_name=row["provider_name"]
        )
        if not existing_provider:
            ai_provider_create = ai_provider_schema.AIProviderCreate(
                name=row["provider_name"]
            )
            ai_provider_crud.create_provider(db, ai_provider_create)


def store_default_api_models(db: Session, csv_path: str) -> None:
    data = load_from_csv(csv_path)
    for row in data:
        existing_api_model = api_model_crud.get_api_model_by_name_and_provider(
            db, api_model_name=row["api_model_name"], provider_name=row["provider_name"]
        )
        if not existing_api_model:
            api_model_create = api_model_schema.APIModelCreate(
                api_model_name=row["api_model_name"],
                alias=row.get("alias"),
                provider_name=row["provider_name"],
            )
            api_model_crud.create_api_model(db, api_model_create)


def store_default_api_key(db: Session) -> None:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    default_key_name = "OPENAI_API_KEY"
    if openai_api_key:
        super_user = user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
        existing_key = user_api_key_crud.get_user_api_key(
            db,
            super_user.id,
            provider_id=ai_provider_crud.get_provider_by_name(db, "OpenAI").id,
            key_name=default_key_name,
        )

        if not existing_key:
            user_api_key_create = user_api_key_schema.UserAPIKeyCreate(
                user_id=super_user.id,
                provider_id=ai_provider_crud.get_provider_by_name(db, "OpenAI").id,
                name=default_key_name,
                api_key=encrypt_api_key(openai_api_key),
            )
            user_api_key_crud.create_user_api_key(db, user_api_key_create)
