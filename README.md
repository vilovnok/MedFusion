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

## Run backend
Make sure that the agent is working correctly.
FastAPI
```bash
./run.sh fastapi
```
