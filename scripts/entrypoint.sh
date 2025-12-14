#!/usr/bin/env sh
set -eu

echo "[entrypoint] DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-musiclib.settings}"

# Wait for Postgres if configured
if [ "${DJANGO_DB_ENGINE:-django.db.backends.postgresql}" = "django.db.backends.postgresql" ]; then
  echo "[entrypoint] Waiting for PostgreSQL at ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432} ..."
  python - <<'PY'
import os, time
import psycopg2

host = os.getenv('POSTGRES_HOST', 'db')
port = int(os.getenv('POSTGRES_PORT', '5432'))
name = os.getenv('POSTGRES_DB', 'musiclib')
user = os.getenv('POSTGRES_USER', 'musiclib')
pwd  = os.getenv('POSTGRES_PASSWORD', 'musiclib')

deadline = time.time() + 60
last_err = None
while time.time() < deadline:
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=name, user=user, password=pwd)
        conn.close()
        print('[entrypoint] PostgreSQL is ready')
        raise SystemExit(0)
    except Exception as e:
        last_err = e
        time.sleep(1)

print('[entrypoint] PostgreSQL not ready after 60s:', last_err)
raise SystemExit(1)
PY
fi

echo "[entrypoint] Applying migrations..."
python manage.py migrate --noinput

if [ "${DJANGO_COLLECTSTATIC:-1}" = "1" ]; then
  echo "[entrypoint] Collecting static files..."
  python manage.py collectstatic --noinput
fi

if [ "${DJANGO_SUPERUSER_CREATE:-0}" = "1" ]; then
  echo "[entrypoint] Creating superuser (if missing)..."
  python manage.py shell -c "\
import os;\
from django.contrib.auth import get_user_model;\
User=get_user_model();\
u=os.getenv('DJANGO_SUPERUSER_USERNAME','admin');\
e=os.getenv('DJANGO_SUPERUSER_EMAIL','admin@example.com');\
p=os.getenv('DJANGO_SUPERUSER_PASSWORD','admin');\
User.objects.filter(username=u).exists() or User.objects.create_superuser(u,e,p)" || true
fi

case "${DJANGO_RUN_MODE:-dev}" in
  dev)
    echo "[entrypoint] Starting Django dev server..."
    exec python manage.py runserver 0.0.0.0:8000
    ;;
  gunicorn)
    echo "[entrypoint] Starting Gunicorn..."
    exec gunicorn musiclib.wsgi:application --bind 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-3}" --timeout "${GUNICORN_TIMEOUT:-60}"
    ;;
  *)
    echo "[entrypoint] Unknown DJANGO_RUN_MODE=${DJANGO_RUN_MODE}. Use 'dev' or 'gunicorn'." >&2
    exit 2
    ;;
esac
