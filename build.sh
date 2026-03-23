#!/bin/bash
# Build script for Render deployment

set -o errexit

# Install dependencies
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
