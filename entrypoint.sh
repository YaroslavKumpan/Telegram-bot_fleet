#!/bin/bash
set -e

echo "Ожидание PostgreSQL..."
until python manage.py check --database default; do
  echo "PostgreSQL ещё не готов, ждём..."
  sleep 1
done
echo "PostgreSQL готов!"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"