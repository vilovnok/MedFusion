#!/bin/bash

if [ "$1" == "celery" ]; then
    poetry run celery --app=backend.worker.tasks worker --loglevel=info
elif [ "$1" == "fastapi" ]; then
    poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
elif [ "$1" == "agent" ]; then
    poetry run python agent/main.py
fi