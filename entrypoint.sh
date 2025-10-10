#!/bin/sh
set -e

# Wait for DB to be available
until nc -z "$DATABASE_HOST" 3306; do
  echo "Waiting for database at $DATABASE_HOST:3306..."
  sleep 1
done

echo "Database is up - continuing..."

# Apply migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
