"""Add domain column to prompts

Revision ID: c1a2b3d4e5f6
Revises: aa34664b3455
Create Date: 2026-03-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

domain_type_enum = sa.Enum('ielts', 'ksat', name='domaintype')

# revision identifiers, used by Alembic.
revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, None] = 'aa34664b3455'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    domain_type_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'prompts',
        sa.Column(
            'domain',
            domain_type_enum,
            nullable=False,
            server_default='ielts',
        ),
    )


def downgrade() -> None:
    op.drop_column('prompts', 'domain')
    domain_type_enum.drop(op.get_bind(), checkfirst=True)
