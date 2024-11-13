# MedFusion

First make sure that you have launched 
```bash
poetry install

poetry shell
```

## Run all microservers
```bash
docker compose up -d rabbitmq redis qdrant
```

## Run backend
```bash
chmod +x script_name.sh
```
Make sure that the agent is working correctly.
```bash
./run.sh agent
```
FastAPI
```bash
./run.sh fastapi
```
Celery
```bash
./run.sh celery
```
