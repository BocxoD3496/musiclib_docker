#!/usr/bin/env sh
set -e

# Small DB wait (works without pg_isready)
echo "Waiting for PostgreSQL..."
python - <<'PY'
import os, time, socket
host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))
deadline = time.time() + 60
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print("PostgreSQL is reachable.")
            break
    except OSError:
        time.sleep(2)
else:
    raise SystemExit("PostgreSQL not reachable within timeout.")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

# Development-friendly: runserver serves static/media.
python manage.py runserver 0.0.0.0:8000
