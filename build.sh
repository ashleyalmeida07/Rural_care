#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip

# Check if we should use lightweight requirements (for Render free tier)
if [ "$USE_LIGHTWEIGHT_DEPS" = "true" ]; then
    echo "Installing lightweight dependencies (ML features disabled)..."
    pip install -r requirements-render.txt
else
    echo "Installing full dependencies..."
    pip install -r requirements.txt
fi

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate
