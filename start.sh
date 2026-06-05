#!/usr/bin/env bash
# Arranque en Render: migraciones + catálogo demo + gunicorn.
set -o errexit

echo "==> Ejecutando migraciones..."
python manage.py migrate --noinput

echo "==> Poblando catálogo (idempotente)..."
python manage.py seed_catalog

echo "==> Iniciando gunicorn..."
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
