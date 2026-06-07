#!/bin/bash
# Stop script on error
set -e

echo "Running Database Migrations..."
alembic upgrade head

echo "Starting the application..."
# Check ENVIRONMENT variable to determine server type
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running in PRODUCTION mode (Gunicorn)..."
    exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.app.main:app --bind 0.0.0.0:8000
else
    echo "Running in DEVELOPMENT mode (Uvicorn)..."
    exec uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
fi