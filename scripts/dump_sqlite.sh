#!/usr/bin/env sh
set -eu

# Dumps data from SQLite (default Django config) into a JSON fixture.
# Usage: ./scripts/dump_sqlite.sh sqlite_dump.json

OUT=${1:-sqlite_dump.json}
python manage.py dumpdata --indent 2 --natural-foreign --natural-primary \
  -e contenttypes -e auth.Permission > "$OUT"
echo "Dump written to $OUT"
