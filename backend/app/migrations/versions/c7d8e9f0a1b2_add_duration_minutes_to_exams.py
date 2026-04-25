"""Add duration_minutes to exams

Adds a nullable duration_minutes column so each exam can declare its own
time limit (e.g. 120 for CAU/Inha humanities). Seeded rows that predate
the column are backfilled for universities whose time limit is known;
unknown combinations stay NULL and the frontend hides the timer.

Revision ID: c7d8e9f0a1b2
Revises: b6c7d8e9f0a1
Create Date: 2026-04-25 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, None] = "b6c7d8e9f0a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "exams",
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
    )
    op.execute(
        """
        UPDATE exams
           SET duration_minutes = 120
         WHERE university IN ('중앙대학교', '인하대학교')
           AND track = 'humanities'
        """
    )


def downgrade() -> None:
    op.drop_column("exams", "duration_minutes")
