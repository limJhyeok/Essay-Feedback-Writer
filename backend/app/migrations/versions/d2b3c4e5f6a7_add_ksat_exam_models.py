"""Add KSAT exam models (Exam, Passage, ExamQuestion)

Revision ID: d2b3c4e5f6a7
Revises: c1a2b3d4e5f6
Create Date: 2026-03-28 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

track_type_enum = postgresql.ENUM('humanities', 'sciences', name='tracktype', create_type=False)
domain_type_enum = postgresql.ENUM('ielts', 'ksat', name='domaintype', create_type=False)

# revision identifiers, used by Alembic.
revision: str = 'd2b3c4e5f6a7'
down_revision: Union[str, None] = 'c1a2b3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tracktype enum (new); domaintype already exists from previous migration
    bind = op.get_bind()
    postgresql.ENUM('humanities', 'sciences', name='tracktype').create(bind, checkfirst=True)

    op.create_table(
        'exams',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('domain', domain_type_enum, nullable=False, server_default='ksat'),
        sa.Column('university', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('track', track_type_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )

    op.create_table(
        'passages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('exam_id', sa.Integer(), sa.ForeignKey('exams.id'), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table(
        'exam_questions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('exam_id', sa.Integer(), sa.ForeignKey('exams.id'), nullable=False),
        sa.Column('prompt_id', sa.Integer(), sa.ForeignKey('prompts.id'), nullable=False),
        sa.Column('question_number', sa.Integer(), nullable=False),
        sa.Column('max_points', sa.Integer(), nullable=False),
        sa.Column('char_min', sa.Integer(), nullable=True),
        sa.Column('char_max', sa.Integer(), nullable=True),
        sa.Column('passage_refs', sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('exam_questions')
    op.drop_table('passages')
    op.drop_table('exams')
    postgresql.ENUM(name='tracktype').drop(op.get_bind(), checkfirst=True)
