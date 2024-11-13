# MedFusion(backend)

## Run FastApi
```bash
uvicorn backend.main:app  --reload
```

## Run Celery with ReabbitMQ

```bash
celery --app=backend.worker.tasks worker --loglevel=info
```