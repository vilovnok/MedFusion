#!/bin/bash

echo "Starting Docker Compose..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "Error starting Docker Compose. Check your docker-compose.yml configuration."
    exit 1
fi

echo "Inserting data into PostgreSQL..."
poetry run python -m backend.src.migration.main --action create

if [ $? -ne 0 ]; then
    echo "Error inserting data into PostgreSQL."
    exit 1
fi

echo "Starting FastAPI agent..."
poetry run gunicorn -w 8 -k uvicorn.workers.UvicornWorker backend.src.main:app --bind 0.0.0.0:8000 --timeout 360


if [ $? -ne 0 ]; then
    echo "Error starting FastAPI. Check your application code."
    exit 1
fi

echo "Services started successfully."