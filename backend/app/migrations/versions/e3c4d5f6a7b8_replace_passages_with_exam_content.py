"""Replace passages table with exam content field

Revision ID: e3c4d5f6a7b8
Revises: d2b3c4e5f6a7
Create Date: 2026-03-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e3c4d5f6a7b8'
down_revision: Union[str, None] = 'd2b3c4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add content column to exams
    op.add_column('exams', sa.Column('content', sa.Text(), nullable=True))

    # 2. Migrate passage data into exam content
    op.execute("""
        UPDATE exams SET content = (
            SELECT string_agg(
                E'(' || p.label || E') ' || p.content,
                E'\n\n' ORDER BY p."order"
            )
            FROM passages p WHERE p.exam_id = exams.id
        )
    """)

    # 3. Drop passages table
    op.drop_table('passages')


def downgrade() -> None:
    # Recreate passages table
    op.create_table(
        'passages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('exam_id', sa.Integer(), sa.ForeignKey('exams.id'), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
    )

    # Drop content column from exams
    op.drop_column('exams', 'content')
