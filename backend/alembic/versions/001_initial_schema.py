"""Initial schema - user, post, postview tables

Revision ID: 001_initial
Revises: None
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- User table ---
    op.create_table(
        "user",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=True),
        sa.Column("avatar", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=False, server_default="admin"),
        sa.Column("provider", sa.String(), nullable=False, server_default="local"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    # --- Post table ---
    op.create_table(
        "post",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("summary", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("cover_image", sa.String(), nullable=True),
        sa.Column("source_urls", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("tags", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="published"),
        sa.Column("search_vector", sa.Text(), nullable=True),  # tsvector added by trigger migration
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_post_slug", "post", ["slug"], unique=True)

    # --- PostView table ---
    op.create_table(
        "postview",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("post_id", UUID(as_uuid=True), sa.ForeignKey("post.id"), nullable=False),
        sa.Column("viewed_at", sa.DateTime(), nullable=False),
        sa.Column("user_agent", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("postview")
    op.drop_table("post")
    op.drop_table("user")
