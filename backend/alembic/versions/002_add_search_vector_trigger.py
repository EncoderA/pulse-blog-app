"""Add search_vector tsvector column, trigger, and GIN index

Revision ID: 002_search_vector
Revises: 001_initial
Create Date: 2024-01-01 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_search_vector"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alter the search_vector column to be a proper tsvector type
    op.execute("ALTER TABLE post DROP COLUMN IF EXISTS search_vector")
    op.execute("ALTER TABLE post ADD COLUMN search_vector tsvector")

    # Create the trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_search_vector()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.search_vector :=
            to_tsvector('english',
              coalesce(NEW.title, '') || ' ' ||
              coalesce(NEW.summary, '') || ' ' ||
              coalesce(NEW.content, '')
            );
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create the trigger
    op.execute("""
        CREATE TRIGGER post_search_vector_update
        BEFORE INSERT OR UPDATE ON post
        FOR EACH ROW EXECUTE FUNCTION update_search_vector();
    """)

    # Create the GIN index for fast full-text search
    op.execute("""
        CREATE INDEX post_search_idx ON post USING GIN(search_vector);
    """)

    # Backfill existing rows
    op.execute("""
        UPDATE post SET search_vector =
            to_tsvector('english',
              coalesce(title, '') || ' ' ||
              coalesce(summary, '') || ' ' ||
              coalesce(content, '')
            );
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS post_search_vector_update ON post")
    op.execute("DROP FUNCTION IF EXISTS update_search_vector()")
    op.execute("DROP INDEX IF EXISTS post_search_idx")
    op.execute("ALTER TABLE post DROP COLUMN IF EXISTS search_vector")
