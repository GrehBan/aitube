# File: src/app/tasks/worker.py
# Description: Celery app configuration

from celery import Celery
from src.app.config import settings

celery_app = Celery("aitube_worker", broker=settings.CELERY_BROKER_URL)
celery_app.conf.task_routes = {"src.app.tasks.video_tasks.*": "main-queue"}