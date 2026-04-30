"""rename blog_visitor.visite_date to visit_date

Revision ID: 0002_rename_visit_date
Revises: 0001_initial
Create Date: 2026-04-30 07:05:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0002_rename_visit_date'
down_revision: Union[str, Sequence[str], None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('blog_visitor', 'visite_date', new_column_name='visit_date')


def downgrade() -> None:
    op.alter_column('blog_visitor', 'visit_date', new_column_name='visite_date')
