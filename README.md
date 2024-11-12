# MedFusion


## Run all microservers
```bash
docker compose up -d
```
## Run Celery with ReabbitMQ

```bash
celery --app=backend.worker.tasks worker --loglevel=info
```