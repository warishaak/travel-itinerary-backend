#!/bin/bash
# Build script for Render deployment

set -o errexit

# Install dependencies from root
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create admin user
python manage.py create_admin
