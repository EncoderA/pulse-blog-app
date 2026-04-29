-- Full-text search trigger
-- Run this in your PostgreSQL database after the tables are created

CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector :=
    to_tsvector('english',
      coalesce(NEW.title, '') || ' ' ||
      coalesce(NEW.summary, '') || ' ' ||
      coalesce(NEW.main_content, '')
    );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER post_search_vector_update
BEFORE INSERT OR UPDATE ON post
FOR EACH ROW EXECUTE FUNCTION update_search_vector();

CREATE INDEX IF NOT EXISTS post_search_idx ON post USING GIN(search_vector);
