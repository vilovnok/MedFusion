#!/bin/bash

echo "Setup Docker Compose..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "Ошибка при запуске Docker Compose. Проверьте конфигурацию docker-compose.yml."
    exit 1
fi

echo "Install poetry"
pip install poetry

echo "Setup libs"
poetry install
poetry shell

echo "Insert data to PostgreSQL..."
poetry run python -m backend.src.migration.main --action create

echo "Setup Agent..."
poetry run python -m backend.src.main


if [ $? -ne 0 ]; then
    echo "Ошибка при запуске FastAPI. Проверьте код вашего приложения."
    exit 1
fi