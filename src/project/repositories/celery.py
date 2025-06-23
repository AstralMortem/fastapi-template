from typing import Annotated, Callable
from celery import Celery
from fastapi import Depends
from project.config import settings


class CeleryRepository:
    def __init__(self, backend_url: str, broker_url: str, **kwargs):
        self._celery = Celery(
            "worker", backend=backend_url, broker=broker_url, **kwargs
        )

    @property
    def worker(self):
        return self._celery

    def wrap_task(self, func: Callable):
        return self.worker.task(func)

    def send_task(self, func: Callable, *args, **kwargs):
        return func.delay(*args, **kwargs)


def get_celery_repository():
    return CeleryRepository(settings.CELERY_BACKEND_URL, settings.CELERY_BROKER_URL)


CeleryRepoDep = Annotated[CeleryRepository, Depends(get_celery_repository)]
