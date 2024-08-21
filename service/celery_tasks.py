import asyncio
import json

import reverse_geocode
from geopy.distance import geodesic
from itertools import combinations
from celery import shared_task

from db.models import StatusEnum
from db.tasks import get_all_coordinates_for_task, create_point, update_task_status, create_link


@shared_task(queue='celery', name='set_reverse_geocoding')
def set_reverse_geocoding(*args, **kwargs) -> None:
    loop = asyncio.get_event_loop()
    db_task_id = kwargs["db_task_id"]

    all_coordinates = loop.run_until_complete(get_all_coordinates_for_task(db_task_id))
    for coordinates in all_coordinates:
        reverse_geocode_result = reverse_geocode.get((coordinates.latitude, coordinates.longitude))
        loop.run_until_complete(create_point(name=coordinates.country, address=json.dumps(reverse_geocode_result),
                                             task_id=db_task_id))


@shared_task(queue='celery', name='set_links')
def set_links(*args, **kwargs) -> None:
    loop = asyncio.get_event_loop()
    db_task_id = kwargs["db_task_id"]
    all_coordinates = loop.run_until_complete(get_all_coordinates_for_task(db_task_id))

    coord_pairs = list(combinations(all_coordinates, 2))
    for pair in coord_pairs:
        source_point = pair[0]
        destination_point = pair[1]
        distance = geodesic((source_point.latitude, source_point.longitude),
                            (destination_point.latitude, destination_point.longitude)).miles
        loop.run_until_complete(create_link(name=f"{source_point.country}{destination_point.country}",
                                            distance=str(distance),
                                            task_id=db_task_id))
    loop.run_until_complete(update_task_status(task_id=db_task_id, status=StatusEnum.DONE))


@shared_task(queue='celery', name='task_main')
def task_main(*args, **kwargs):
    db_task_id = kwargs["db_task_id"]
    chain = (set_reverse_geocoding.s(db_task_id=db_task_id) | set_links.s(db_task_id=db_task_id))
    chain()
