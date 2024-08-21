import os

from celery import Celery


redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

app = Celery(__name__, broker=redis_url, backend=redis_url, include=['service.celery_tasks'])
