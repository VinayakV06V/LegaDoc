"""
SQLAlchemy engine/session setup. No Alembic yet — at this baseline stage, run
`python -m app.init_db` to create tables directly from the models below.
Add Alembic migrations once the schema stabilizes past the first sprint.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session, always closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
