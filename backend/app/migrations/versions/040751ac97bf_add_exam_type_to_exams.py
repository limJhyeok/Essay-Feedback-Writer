"""add exam_type to exams

Revision ID: 040751ac97bf
Revises: e3c4d5f6a7b8
Create Date: 2026-03-29 07:17:34.813331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '040751ac97bf'
down_revision: Union[str, None] = 'e3c4d5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    examtype = sa.Enum('mock', 'official', name='examtype')
    examtype.create(op.get_bind(), checkfirst=True)
    op.add_column('exams', sa.Column('exam_type', examtype, server_default='official', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('exams', 'exam_type')
    sa.Enum(name='examtype').drop(op.get_bind(), checkfirst=True)
