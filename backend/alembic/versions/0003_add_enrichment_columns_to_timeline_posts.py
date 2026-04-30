"""add enrichment tracking columns to timeline_posts

Revision ID: 0003_add_enrichment_columns
Revises: 0002_rename_visit_date
Create Date: 2026-04-30 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0003_add_enrichment_columns'
down_revision: Union[str, Sequence[str], None] = '0002_rename_visit_date'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'timeline_posts',
        sa.Column('retry_count', sa.SmallInteger(), nullable=False, server_default='0'),
    )
    op.add_column(
        'timeline_posts',
        sa.Column('enriched_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        'timeline_posts',
        sa.Column('enrichment_model', sa.String(100), nullable=True),
    )
    op.add_column(
        'timeline_posts',
        sa.Column('agent_config_id', sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('timeline_posts', 'agent_config_id')
    op.drop_column('timeline_posts', 'enrichment_model')
    op.drop_column('timeline_posts', 'enriched_at')
    op.drop_column('timeline_posts', 'retry_count')
