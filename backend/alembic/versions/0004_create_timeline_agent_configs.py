"""create timeline_agent_configs table

Revision ID: 0004_create_timeline_agent_configs
Revises: 0003_add_enrichment_columns
Create Date: 2026-04-30 18:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '0004_create_agent_configs'
down_revision: Union[str, Sequence[str], None] = '0003_add_enrichment_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'timeline_agent_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('context_name', sa.String(100), nullable=False),
        sa.Column('custom_instructions', sa.Text(), nullable=True),
        sa.Column('focus_topics', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('tone', sa.String(30), nullable=False, server_default='neutral'),
        sa.Column('analysis_depth', sa.String(20), nullable=False, server_default='standard'),
        sa.Column('llm_model_override', sa.String(100), nullable=True),
        sa.Column('auto_enrich', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('timeline_agent_configs')
