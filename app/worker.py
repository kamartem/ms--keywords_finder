import logging
import os

from celery import Celery
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import TORTOISE_ORM
LOG = logging.getLogger(__name__)

CELERY_BROKER_URL = (os.environ.get("CELERY_BROKER_URL", "redis://redis:6379"), )
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")

celery_app = Celery('celery_worker', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery_app.autodiscover_tasks(['app.keywords'])

celery_app.conf.timezone = 'Europe/Moscow'
celery_app.conf.task_routes = {"keywords.tasks.test_celery": "test-queue"}
celery_app.conf.update(task_track_started=True)



@celery_app.task
def add(x, y):
    res = x + y
    LOG.info("Adding %s + %s, res: %s" % (x, y, res))
    return res
