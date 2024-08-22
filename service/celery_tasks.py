import asyncio
import json
from itertools import combinations
from uuid import UUID

import reverse_geocode
from celery import shared_task
from geopy.distance import geodesic

from db.models import StatusEnum, Point, Link
from db.tasks import get_all_coordinates_for_task, update_task_status, bulk_create


@shared_task(name='set_reverse_geocoding')
def set_reverse_geocoding(*args, **kwargs) -> None:
    task_id = kwargs["task_id"]
    all_coordinates = asyncio.run(get_all_coordinates_for_task(task_id))
    coord_list = list()

    for coordinates in all_coordinates:
        reverse_geocode_result = reverse_geocode.get((coordinates.latitude,
                                                      coordinates.longitude))

        coord_list.append(Point(name=coordinates.country,
                                address=json.dumps(reverse_geocode_result),
                                task_id=task_id))

    asyncio.run(bulk_create(coord_list))


@shared_task(name='set_links')
def set_links(*args, **kwargs) -> None:
    task_id = kwargs["task_id"]
    all_coordinates = asyncio.run(get_all_coordinates_for_task(task_id))
    coord_pairs = list(combinations(all_coordinates, 2))
    link_list = list()

    for pair in coord_pairs:
        source_point = pair[0]
        destination_point = pair[1]

        distance = geodesic((source_point.latitude, source_point.longitude),
                            (destination_point.latitude, destination_point.longitude)).miles

        link_list.append(Link(name=f"{source_point.country}{destination_point.country}",
                              distance=str(distance),
                              task_id=task_id))

    asyncio.run(bulk_create(link_list))
    asyncio.run(update_task_status(task_id=task_id,
                                   status=StatusEnum.DONE))


@shared_task(name='task_main')
def task_main(task_id: UUID) -> None:
    chain = (set_reverse_geocoding.s(task_id=task_id) | set_links.s(task_id=task_id))
    chain()
