#!/usr/bin/env sh
set -eu

# Loads a JSON fixture into PostgreSQL (expects Docker Compose services).
# Usage: ./scripts/load_postgres.sh sqlite_dump.json

FIXTURE=${1:-sqlite_dump.json}

if [ ! -f "$FIXTURE" ]; then
  echo "Fixture file not found: $FIXTURE" >&2
  exit 1
fi

docker compose run --rm web python manage.py loaddata "/app/$FIXTURE"
