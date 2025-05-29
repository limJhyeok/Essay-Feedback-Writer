import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    prompts = relationship("Prompt", back_populates="creator")
    essays = relationship("Essay", back_populates="author")
    feedbacks = relationship("Feedback", back_populates="user")

    prompt_reactions = relationship("PromptReaction", back_populates="user")
    essay_reactions = relationship("EssayReaction", back_populates="user")
    feedback_reactions = relationship("FeedbackReaction", back_populates="user")
    api_keys = relationship(
        "UserAPIKey", back_populates="user", cascade="all, delete-orphan"
    )


class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=True)
    description = Column(String, nullable=True)
    deprecated = Column(Boolean, default=False)
    registered_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    hosted_by = relationship("APIModel", back_populates="bot")
    feedbacks = relationship("Feedback", back_populates="bot")


class APIModel(Base):
    __tablename__ = "api_models"

    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    provider_id = Column(Integer, ForeignKey("ai_providers.id"))

    api_model_name = Column(String, nullable=False)
    alias = Column(String, nullable=True)
    deprecated = Column(Boolean, default=False)
    registered_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    bot = relationship("Bot", back_populates="hosted_by")
    provider = relationship("AIProvider", back_populates="hosts")

    __table_args__ = (
        UniqueConstraint(
            "bot_id", "provider_id", "api_model_name", name="uix_model_provider_api"
        ),
    )


class AIProvider(Base):
    __tablename__ = "ai_providers"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # e.g. "OpenAI", "Anthropic"
    deprecated = Column(Boolean, default=False)
    registered_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    hosts = relationship("APIModel", back_populates="provider")
    user_keys = relationship("UserAPIKey", back_populates="provider")


def generate_key_name():
    return f"secret-key_{datetime.now(timezone.utc).isoformat()}"


class UserAPIKey(Base):
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=False)
    name = Column(String, default=generate_key_name, nullable=False)
    api_key = Column(String, nullable=False)
    registered_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_used = Column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="api_keys")
    provider = relationship("AIProvider", back_populates="user_keys")


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    creator = relationship("User", back_populates="prompts")
    essays = relationship("Essay", back_populates="prompt")
    reactions = relationship("PromptReaction", back_populates="prompt")
    feedbacks = relationship("Feedback", back_populates="prompt")


class Essay(Base):
    __tablename__ = "essays"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prompt_id = Column(Integer, ForeignKey("prompts.id"))
    content = Column(Text, nullable=False)
    submitted_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    # submitted_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)

    author = relationship("User", back_populates="essays")
    prompt = relationship("Prompt", back_populates="essays")
    feedbacks = relationship("Feedback", back_populates="essay")


class ExampleEssay(Base):
    __tablename__ = "example_essays"

    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    prompt = relationship("Prompt", backref="example_essays")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"))
    essay_id = Column(Integer, ForeignKey("essays.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    bot_id = Column(Integer, ForeignKey("bots.id"))
    content = Column(JSONB, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    prompt = relationship("Prompt", back_populates="feedbacks")
    essay = relationship("Essay", back_populates="feedbacks")
    user = relationship("User", back_populates="feedbacks")
    bot = relationship("Bot", back_populates="feedbacks")


class ReactionType(enum.Enum):
    like = "like"
    dislike = "dislike"


class EssayReaction(Base):
    __tablename__ = "essay_reactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    essay_id = Column(Integer, ForeignKey("essays.id"), nullable=False)
    reaction = Column(Enum(ReactionType), nullable=False)
    reacted_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)

    essay = relationship("Essay", backref="reactions")
    user = relationship("User", back_populates="essay_reactions")

    __table_args__ = (
        UniqueConstraint("user_id", "essay_id", name="unique_user_essay_reaction"),
    )


class PromptReaction(Base):
    __tablename__ = "prompt_reactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    reaction = Column(Enum(ReactionType), nullable=False)
    reacted_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)

    prompt = relationship("Prompt", back_populates="reactions")
    user = relationship("User", back_populates="prompt_reactions")

    __table_args__ = (
        UniqueConstraint("user_id", "prompt_id", name="unique_user_prompt_reaction"),
    )


class FeedbackReaction(Base):
    __tablename__ = "feedback_reactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id"), nullable=False)
    reaction = Column(Enum(ReactionType), nullable=False)
    reacted_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)

    feedback = relationship("Feedback", backref="reactions")
    user = relationship("User", back_populates="feedback_reactions")

    __table_args__ = (
        UniqueConstraint(
            "user_id", "feedback_id", name="unique_user_feedback_reaction"
        ),
    )


class RubricScoringMethod(enum.Enum):
    average = "average"
    weighted_sum = "weighted_sum"
    sum = "sum"


class LanguageType(enum.Enum):
    korea = "ko"
    english = "en"


class Rubric(Base):
    __tablename__ = "rubrics"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    subject = Column(Text, nullable=False)
    language = Column(Enum(LanguageType), nullable=False)
    description = Column(Text, nullable=True)
    scoring_method = Column(Enum(RubricScoringMethod), nullable=False)
    weights = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    criteria = relationship("RubricCriterion", back_populates="rubric")


class RubricCriterion(Base):
    __tablename__ = "rubric_criteria"

    id = Column(Integer, primary_key=True)
    rubric_id = Column(Integer, ForeignKey("rubrics.id"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)

    rubric = relationship("Rubric", back_populates="criteria")
