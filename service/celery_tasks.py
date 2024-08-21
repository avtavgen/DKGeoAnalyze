import asyncio

from celery import shared_task
from pydantic import BaseModel
from celery.result import AsyncResult

from db.tasks import read_celery_task


class TaskOut(BaseModel):
    id: str
    status: str


def _to_task_out(r: AsyncResult) -> TaskOut:
    return TaskOut(id=r.task_id, status=r.status)


@shared_task(queue='celery', name='task_a')
def task_a(*args, **kwargs):
    loop = asyncio.get_event_loop()
    db_task_id = kwargs["db_task_id"]
    db_task = loop.run_until_complete(read_celery_task(db_task_id))
    for i in range(10):
        print(f"Task A: {i}, task_id: {db_task.id}, status: {db_task.status}")


@shared_task(queue='celery', name='task_b')
def task_b(*args, **kwargs):
    loop = asyncio.get_event_loop()
    db_task_id = kwargs["db_task_id"]
    db_task = loop.run_until_complete(read_celery_task(db_task_id))
    for i in range(10):
        print(f"Task B: {i}, task_id: {db_task.id}, status: {db_task.status}")


@shared_task(queue='celery', name='task_main')
def task_main(*args, **kwargs):
    db_task_id = kwargs["db_task_id"]
    chain = (task_a.s(db_task_id=db_task_id) | task_b.s(db_task_id=db_task_id))
    chain()
