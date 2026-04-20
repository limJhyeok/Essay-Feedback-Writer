import logging

from sqlalchemy.ext.asyncio import AsyncSession

import os
import csv
from typing import Any
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
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
from app.models import DomainType, Exam, ExamQuestion, ExampleEssay, Prompt, TrackType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

async_engine = create_async_engine(str(settings.ASYNC_SQLALCHEMY_DATABASE_URI))
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db(db: AsyncSession) -> None:
    user = await user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
    if not user:
        user_create = user_schema.UserCreate(
            email=settings.FIRST_SUPERUSER,
            is_superuser=True,
            password=settings.FIRST_SUPERUSER_PASSWORD,
        )
        await user_crud.create_user(db, user_create)


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


async def store_example_essays(db: AsyncSession, csv_path: str) -> None:
    data = load_from_csv(csv_path)
    super_user = await user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
    for item in data:
        prompt_content = item["prompt"].strip()
        example_answer = item["example_answer"].strip()

        existing_prompt = await prompt_crud.get_prompt_by_content(
            db, content=prompt_content
        )
        if not existing_prompt:
            prompt_create = prompt_schema.PromptCreate(
                content=prompt_content,
                created_by=super_user.id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db_prompt = await prompt_crud.create_prompt(db, prompt_create)

            existing_example = await example_essay_crud.get_example_essay_by_content(
                db, example_answer
            )
            if not existing_example:
                example_essay_create = example_essay_schema.ExampleEssayCreate(
                    prompt_id=db_prompt.id,
                    content=example_answer,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

                _ = await example_essay_crud.create_example_essay(
                    db, example_essay_create
                )


async def store_default_rubric(
    db: AsyncSession, csv_path: str, rubric_create: rubric_schema.RubricCreate
) -> None:
    data = load_from_csv(csv_path)
    existing_rubric = await rubric_crud.get_rubric_by_name(db, rubric_create.name)
    if not existing_rubric:
        super_user = await user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)
        rubric_create.created_by = super_user.id
        db_rubric = await rubric_crud.create_rubric(db, rubric_create)

        for row in data:
            score = row.pop("score")
            try:
                score = int(score)
            except ValueError:
                logger.error(f"Invalid score value '{score}' encountered.")

            for _criterion_name, _description in row.items():
                existing_criterion = (
                    await rubric_criterion_crud.get_criterion_by_name_and_score(
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
                    _ = await rubric_criterion_crud.create_rubric_criterion(
                        db, criterion_create
                    )


async def store_default_bots(db: AsyncSession, csv_path: str) -> None:
    data = load_from_csv(csv_path)
    for row in data:
        existing_bot = await bot_crud.get_bot_by_name(db, row["name"].strip())
        if not existing_bot:
            bot_create = bot_schema.BotCreate(
                name=row["name"].strip(),
                version=row.get("version").strip(),
                description=row.get("description").strip(),
            )
            await bot_crud.create_bot(db, bot_create)


async def store_default_ai_providers(db: AsyncSession, csv_path: str) -> None:
    data = load_from_csv(csv_path)
    for row in data:
        existing_provider = await ai_provider_crud.get_provider_by_name(
            db, provider_name=row["provider_name"]
        )
        if not existing_provider:
            ai_provider_create = ai_provider_schema.AIProviderCreate(
                name=row["provider_name"]
            )
            await ai_provider_crud.create_provider(db, ai_provider_create)


async def store_default_api_models(db: AsyncSession, csv_path: str) -> None:
    data = load_from_csv(csv_path)
    for row in data:
        existing_api_model = await api_model_crud.get_api_model_by_name_and_provider(
            db, api_model_name=row["api_model_name"], provider_name=row["provider_name"]
        )
        if not existing_api_model:
            api_model_create = api_model_schema.APIModelCreate(
                api_model_name=row["api_model_name"],
                alias=row.get("alias"),
                provider_name=row["provider_name"],
            )
            await api_model_crud.create_api_model(db, api_model_create)


async def store_default_api_key(db: AsyncSession) -> None:
    super_user = await user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)

    api_keys = [
        ("OPENAI_API_KEY", "OpenAI"),
        ("ANTHROPIC_API_KEY", "Anthropic"),
    ]

    for env_var, provider_name in api_keys:
        api_key_value = os.getenv(env_var)
        if not api_key_value:
            continue

        provider = await ai_provider_crud.get_provider_by_name(db, provider_name)
        if not provider:
            continue

        existing_key = await user_api_key_crud.get_user_api_key(
            db,
            super_user.id,
            provider_id=provider.id,
        )

        if not existing_key:
            user_api_key_create = user_api_key_schema.UserAPIKeyCreate(
                user_id=super_user.id,
                provider_id=provider.id,
                name=env_var,
                api_key=encrypt_api_key(api_key_value),
            )
            await user_api_key_crud.create_user_api_key(db, user_api_key_create)


async def store_ksat_exam_data(db: AsyncSession) -> None:
    """Seed every KSAT exam registered in `seed_ksat_data.SEED_EXAMS`.

    For each exam module, reads passage/prompt/example_answer files
    referenced by its QUESTIONS list and populates Exam, Prompt,
    ExamQuestion, ExampleEssay rows. Skips exams already present.
    """
    from sqlalchemy import select

    from app.data.ksat.seed_ksat_data import SEED_EXAMS
    from app.models import ExamType

    super_user = await user_crud.get_user_by_email(db, settings.FIRST_SUPERUSER)

    for seed_module in SEED_EXAMS:
        meta = seed_module.EXAM_META
        track = TrackType(meta["track"])

        exists = await db.execute(
            select(Exam).where(
                Exam.university == meta["university"],
                Exam.year == meta["year"],
                Exam.track == track,
            )
        )
        if exists.scalars().first():
            logger.info(
                "KSAT exam already seeded: %s %s %s — skipping",
                meta["university"],
                meta["year"],
                meta["track"],
            )
            continue

        db_exam = Exam(
            domain=DomainType.ksat,
            university=meta["university"],
            year=meta["year"],
            track=track,
            exam_type=ExamType(meta["exam_type"]),
        )
        db.add(db_exam)
        await db.commit()
        await db.refresh(db_exam)

        for q_data in seed_module.QUESTIONS:
            prompt_text = q_data["prompt_path"].read_text(encoding="utf-8").strip()
            passage_text = q_data["passage_path"].read_text(encoding="utf-8").strip()

            db_prompt = Prompt(
                domain=DomainType.ksat,
                content=prompt_text,
                created_by=super_user.id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(db_prompt)
            await db.commit()
            await db.refresh(db_prompt)

            db_question = ExamQuestion(
                exam_id=db_exam.id,
                prompt_id=db_prompt.id,
                question_number=q_data["question_number"],
                max_points=q_data["max_points"],
                char_min=q_data.get("char_min"),
                char_max=q_data.get("char_max"),
                passage_refs=q_data.get("passage_refs"),
                content=passage_text,
                rubric_name=q_data.get("rubric_name"),
            )
            db.add(db_question)

            example_path = q_data.get("example_answer_path")
            if example_path and example_path.is_file():
                example_text = example_path.read_text(encoding="utf-8").strip()
                if example_text:
                    db.add(ExampleEssay(prompt_id=db_prompt.id, content=example_text))

        await db.commit()
        logger.info(
            "KSAT exam seeded: %s %s %s",
            meta["university"],
            meta["year"],
            meta["track"],
        )
