import asyncio
import json

import reverse_geocode
from celery import shared_task
from pydantic import BaseModel
from celery.result import AsyncResult

from db.models import StatusEnum
from db.tasks import read_celery_task, get_all_coordinates_for_task, create_point, update_task_status


class TaskOut(BaseModel):
    id: str
    status: str


def _to_task_out(r: AsyncResult) -> TaskOut:
    return TaskOut(id=r.task_id, status=r.status)


@shared_task(queue='celery', name='set_reverse_geocoding')
def set_reverse_geocoding(*args, **kwargs) -> None:
    loop = asyncio.get_event_loop()
    db_task_id = kwargs["db_task_id"]
    loop.run_until_complete(update_task_status(task_id=db_task_id, status=StatusEnum.RUNNING))

    all_coordinates = loop.run_until_complete(get_all_coordinates_for_task(db_task_id))
    for coordinates in all_coordinates:
        reverse_geocode_result = reverse_geocode.get((coordinates.latitude, coordinates.longitude))
        print(reverse_geocode_result)
        loop.run_until_complete(create_point(name=coordinates.country, address=json.dumps(reverse_geocode_result),
                                             task_id=db_task_id))


@shared_task(queue='celery', name='set_links')
def set_links(*args, **kwargs) -> None:
    loop = asyncio.get_event_loop()
    db_task_id = kwargs["db_task_id"]
    # db_task = loop.run_until_complete(read_celery_task(db_task_id))
    loop.run_until_complete(update_task_status(task_id=db_task_id, status=StatusEnum.DONE))


@shared_task(queue='celery', name='task_main')
def task_main(*args, **kwargs):
    db_task_id = kwargs["db_task_id"]
    chain = (set_reverse_geocoding.s(db_task_id=db_task_id) | set_links.s(db_task_id=db_task_id))
    chain()
