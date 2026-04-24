#!/usr/bin/env sh
set -e

if [ -f /app/.env ]; then
  echo "Using /app/.env"
fi

if [ "$DJANGO_ENV" = "production" ]; then
  exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000
else
  exec python manage.py runserver 0.0.0.0:8000
fi
