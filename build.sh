#!/usr/bin/env bash
# Build script para Render — instala deps, estáticos, migraciones y catálogo demo.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py seed_catalog
