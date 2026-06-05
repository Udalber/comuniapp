#!/usr/bin/env bash
# Build en Render: solo dependencias y estáticos (sin BD).
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
