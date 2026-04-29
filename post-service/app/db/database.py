# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# DATABASE_URL = "postgresql://postgres:kolli@localhost:5432/news_db"

# engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# # ✅ ADD THIS FUNCTION
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# import os

# DATABASE_URL = os.getenv("POST_DB_URL")

# engine = create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# import os

# DATABASE_URL = os.getenv("POST_DB_URL")

# engine = create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True,
#     connect_args={"sslmode": "require"}  # important for Neon
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("POST_DB_URL")

if not DATABASE_URL:
    raise Exception("POST_DB_URL is missing")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"}   # IMPORTANT for Neon
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()