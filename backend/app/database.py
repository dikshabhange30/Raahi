
# Why do we need these?
# - engine manages the connection between Python and PostgreSQL.
# - SessionLocal creates database sessions for queries and updates.
# - Base will be used later when defining database tables with SQLAlchemy models.
# - get_db() provides a session to API endpoints and closes it after use.

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
