#!/bin/bash

echo "Installing Poetry..."
python -m venv venv
source venv/bin/activate
pip install poetry

if [ $? -ne 0 ]; then
    echo "Error installing Poetry."
    exit 1
fi

echo "Setting up dependencies..."
pip install sqlalchemy
pip install asyncpg
poetry install
poetry shell

if [ $? -ne 0 ]; then
    echo "Error installing dependencies."
    exit 1
fi

echo "Dependencies setup completed successfully."