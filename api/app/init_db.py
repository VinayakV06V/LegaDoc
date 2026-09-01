"""
Creates every table from app.models against DATABASE_URL. Run once after
`docker compose up`:

    docker compose exec api python -m app.init_db

Replace with real Alembic migrations once the schema stabilizes — this is
intentionally the simplest thing that works for a baseline.
"""

from app.database import Base, engine
from app import models  # noqa: F401 — import registers every model on Base.metadata

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
