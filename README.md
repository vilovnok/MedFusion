# MedFusion

First make sure that you have launched 
```bash
poetry install

poetry shell
```

## Run all microservers
```bash
docker compose up -d qdrant
```

## Create tables postgres
```bash
poetry run python -m backend.src.migration.main --action create
poetry run python -m backend.src.migration.main --action drop
```
## Run
```bash
poetry run python -m backend.src.main
```

## Run backend
Make sure that the agent is working correctly.
FastAPI
```bash
./run.sh fastapi
```
