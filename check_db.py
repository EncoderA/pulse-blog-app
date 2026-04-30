from sqlalchemy import create_engine, text
import os

url = os.environ["DATABASE_URL"]
print("DB URL:", url[:70], "...")
engine = create_engine(url)

with engine.connect() as conn:
    # List all tables
    rows = conn.execute(text(
        "SELECT table_schema, table_name FROM information_schema.tables "
        "WHERE table_schema NOT IN ('information_schema','pg_catalog') "
        "ORDER BY table_schema, table_name"
    )).fetchall()
    print(f"\n=== Tables ({len(rows)} total) ===")
    for r in rows:
        print(f"  {r[0]}.{r[1]}")

    # Count rows in key tables if they exist
    table_checks = ["post", "posts", "timeline_posts", "cleaned_articles"]
    print("\n=== Row counts ===")
    for t in table_checks:
        try:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"  {t}: {count} rows")
        except Exception as e:
            print(f"  {t}: not found ({e})")
