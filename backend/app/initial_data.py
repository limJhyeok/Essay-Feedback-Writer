import logging
from sqlalchemy.orm import Session

from app.core.db import (
    engine,
    init_db,
    store_example_essays,
    store_default_rubric,
    store_default_ai_providers,
    store_default_api_key,
    store_default_api_models,
    store_default_bots,
)
from app.schemas import rubric_schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)
        store_example_essays(session, "app/data/ielts/example_essays.csv")

        rubric_create = rubric_schema.RubricCreate(
            name="IELTS Writing Task 2",
            subject="English",
            language="en",
            scoring_method="average",
        )
        store_default_rubric(
            session,
            "app/data/ielts/IELTS_writing_task_2_band_descriptions.csv",
            rubric_create,
        )
        store_default_bots(session, "app/data/bots.csv")
        store_default_ai_providers(session, "app/data/AI_provider.csv")
        store_default_api_models(session, "app/data/API_Model.csv")
        store_default_api_key(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
