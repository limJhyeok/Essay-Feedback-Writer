from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import essay_crud, feedback_crud
from app.models import Bot, Prompt, User
from app.schemas import essay_schema, feedback_schema


async def test_create_feedback(
    db: AsyncSession, test_user: User, test_prompt: Prompt, test_bot: Bot
) -> None:
    essay = await essay_crud.create_essay(
        db,
        essay_schema.EssayCreate(
            user_id=test_user.id,
            prompt_id=test_prompt.id,
            content="Essay for feedback creation test.",
            submitted_at=datetime.now(timezone.utc),
        ),
    )

    feedback_content = {
        "overall_score": 7.0,
        "overall_feedback": "Good essay with clear arguments.",
        "feedback_by_criteria": {
            "Task Response": {"score": 7, "feedback": "Addresses the task well."},
        },
    }
    fb_create = feedback_schema.FeedbackCreate(
        user_id=test_user.id,
        prompt_id=test_prompt.id,
        essay_id=essay.id,
        bot_id=test_bot.id,
        content=feedback_content,
        created_at=datetime.now(timezone.utc),
    )
    result = await feedback_crud.create_feedback(db, fb_create)

    assert result.id is not None
    assert result.user_id == test_user.id
    assert result.essay_id == essay.id
    assert result.bot_id == test_bot.id
    assert result.content == feedback_content


async def test_get_feedbacks_by_user_prompt_essay(
    db: AsyncSession, test_user: User, test_prompt: Prompt, test_bot: Bot
) -> None:
    essay = await essay_crud.create_essay(
        db,
        essay_schema.EssayCreate(
            user_id=test_user.id,
            prompt_id=test_prompt.id,
            content="Essay for feedback retrieval test.",
            submitted_at=datetime.now(timezone.utc),
        ),
    )

    fb_create = feedback_schema.FeedbackCreate(
        user_id=test_user.id,
        prompt_id=test_prompt.id,
        essay_id=essay.id,
        bot_id=test_bot.id,
        content={"overall_score": 6.5, "overall_feedback": "Decent work."},
        created_at=datetime.now(timezone.utc),
    )
    await feedback_crud.create_feedback(db, fb_create)

    result = await feedback_crud.get_feedbacks_by_user_prompt_essay(
        db, test_user.id, test_prompt.id, essay.id
    )

    assert len(result) >= 1
    # Verify bot is eagerly loaded via selectinload
    assert result[0].bot is not None
    assert result[0].bot.name == "TestBot"
    assert result[0].content["overall_score"] == 6.5
