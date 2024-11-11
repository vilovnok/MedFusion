# uvicorn
uvicorn backend.main:app  --reload

# celery
celery --app=backend.worker.tasks worker --loglevel=info