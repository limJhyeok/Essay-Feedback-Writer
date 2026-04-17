"""Add content to exam_questions (copy from exams.content)

Moves passage content ownership from Exam to ExamQuestion. For existing rows,
copies the shared exams.content value into each of its questions. exams.content
is retained as a safety net and dropped in a later migration once read paths
are fully switched over.

Revision ID: f4d5e6a7b8c9
Revises: 040751ac97bf
Create Date: 2026-04-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f4d5e6a7b8c9'
down_revision: Union[str, None] = '040751ac97bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'exam_questions',
        sa.Column('content', sa.Text(), nullable=True),
    )
    op.execute("""
        UPDATE exam_questions
           SET content = exams.content
          FROM exams
         WHERE exams.id = exam_questions.exam_id
           AND exams.content IS NOT NULL
    """)


def downgrade() -> None:
    op.drop_column('exam_questions', 'content')
