"""Drop exam_content column

Passage content has fully moved to ExamQuestion.content (see commit
f4d5e6a7b8c9). Nothing reads exams.content anymore, so the legacy
column is removed. Downgrade re-adds the column as nullable Text but
leaves it NULL — the original per-question content can't be collapsed
back into a single shared blob without lossy heuristics, so recovery
after downgrade is out of scope.

Revision ID: b6c7d8e9f0a1
Revises: a5b6c7d8e9f0
Create Date: 2026-04-19 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b6c7d8e9f0a1"
down_revision: Union[str, None] = "a5b6c7d8e9f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("exams", "content")


def downgrade() -> None:
    op.add_column("exams", sa.Column("content", sa.Text(), nullable=True))
