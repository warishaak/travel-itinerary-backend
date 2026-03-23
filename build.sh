#!/bin/bash
# Build script for Render deployment

set -o errexit

# Install dependencies from root
pip install -r requirements.txt

# Add backend to requirements if it exists
if [ -f backend/requirements.txt ]; then
  pip install -r backend/requirements.txt
fi

# Navigate to backend directory
cd backend

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
