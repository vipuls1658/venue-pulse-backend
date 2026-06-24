#!/usr/bin/env bash
# Container entrypoint: wait for MySQL, apply migrations, then exec the CMD
# (daphne). Running migrations here keeps `docker compose up` a one-command
# start; for a multi-replica deploy you'd move migrations to a release step.
set -euo pipefail

DB_HOST="${DB_HOST:-mysql}"
DB_PORT="${DB_PORT:-3306}"

echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
until nc -z "${DB_HOST}" "${DB_PORT}"; do
    sleep 1
done
echo "MySQL is up."

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Starting: $*"
exec "$@"
