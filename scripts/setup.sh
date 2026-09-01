#!/usr/bin/env bash
# One-time local setup: copy env template, build+start everything, create tables.
set -e

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit it if your local ports/creds differ."
fi

docker compose up -d --build
echo "Waiting for the database to accept connections..."
sleep 5

docker compose exec api python -m app.init_db

echo "Up. API: http://localhost:8000/health   Web: http://localhost:5173   MinIO console: http://localhost:9001"
