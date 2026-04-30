"""initial - create web_visitor and blog_visitor tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # web_visitor: one row per date, tracks total daily web visitors
    op.create_table(
        'web_visitor',
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('visitor_count', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('date'),
    )

    # blog_visitor: one row per (date, blog_id), tracks daily visitors per blog
    op.create_table(
        'blog_visitor',
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('blog_id', sa.String(), nullable=True),
        sa.Column('visitor_count', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('date', 'blog_id'),
    )


def downgrade() -> None:
    op.drop_table('blog_visitor')
    op.drop_table('web_visitor')
