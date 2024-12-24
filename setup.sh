#!/bin/bash

# Install Poetry
echo "Installing Poetry..."
python -m venv venv
source venv/bin/activate
pip install poetry

if [ $? -ne 0 ]; then
    echo "Error installing Poetry."
    exit 1
fi

# Install dependencies
echo "Setting up dependencies..."
poetry install

if [ $? -ne 0 ]; then
    echo "Error installing dependencies."
    exit 1
fi

echo "Dependencies setup completed successfully."