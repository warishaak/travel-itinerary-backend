#!/bin/bash
# Build script for Render deployment

set -o errexit

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running migrations..."
python manage.py migrate

echo "==> Creating admin user..."
python manage.py create_admin 2>&1 || echo "Warning: Failed to create admin user"

echo "==> Build complete!"
