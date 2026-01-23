#!/usr/bin/env bash
# Render build script for Rural Care
# This script runs during Render deployment

set -o errexit

echo "=== Rural Care Build Script ==="

# Install Python dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running migrations..."
python manage.py migrate --noinput

echo "=== Build Complete ==="
