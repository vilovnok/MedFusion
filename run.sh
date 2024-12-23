#!/bin/bash

if [ "$1" == "angular" ]; then
    cd frontend
    ng serve
elif [ "$1" == "fastapi" ]; then
    poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
fi