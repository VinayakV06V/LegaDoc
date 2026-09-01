# Database

No Alembic migrations yet at this baseline stage — the schema lives entirely
in `api/app/models.py` (SQLAlchemy). To create tables against a running
Postgres instance:

```bash
docker compose exec api python -m app.init_db
```

Add real Alembic migrations once the schema stabilizes past the first
sprint — trying to version-control a schema that's still moving daily is
more overhead than it's worth right now.

Every table here corresponds to a row in SYSTEM_DESIGN.md's State Ownership
Map — if you need a new piece of persistent state, add it to that table in
the design doc first, then add the model here, not the other way around.
