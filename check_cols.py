from sqlalchemy import create_engine, text
import os
url = os.environ['DATABASE_URL']
engine = create_engine(url)
with engine.connect() as conn:
    rows = conn.execute(text(
        "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='post' ORDER BY ordinal_position"
    )).fetchall()
    for r in rows:
        print(r[0], '-', r[1])
