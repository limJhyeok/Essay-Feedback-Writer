"""Add rubric_name to exam_questions

Lets each ExamQuestion point at the YAML rubric that should score its
essays, replacing the hardcoded `question_number → rubric_name` map
that lived in the frontend. Nullable because some exam seeds may not
have a registered rubric yet (e.g. a seed landing before the rubric
YAML is written).

Revision ID: a5b6c7d8e9f0
Revises: f4d5e6a7b8c9
Create Date: 2026-04-19 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a5b6c7d8e9f0"
down_revision: Union[str, None] = "f4d5e6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "exam_questions",
        sa.Column("rubric_name", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("exam_questions", "rubric_name")
