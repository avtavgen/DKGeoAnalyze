import codecs
import csv
from typing import List
from uuid import UUID

from fastapi import UploadFile
from sqlmodel import select

from db.core import scoped_session
from db.models import Task, NotFoundError, FileData, Point, Link


async def bulk_create(data_list: List[FileData | Point | Link]) -> None:
    async with scoped_session() as session:
        session.add_all(data_list)
        await session.commit()


async def get_or_create_task(task_id: UUID = None) -> Task:
    async with scoped_session() as session:
        task = await session.get(Task, task_id)
        if task is None:
            task = Task()
            session.add(task)
            await session.commit()
            await session.refresh(task)
        return task


async def update_task_status(task_id: UUID, status: str) -> None:
    async with scoped_session() as session:
        task = await session.get(Task, task_id)
        if task is None:
            raise NotFoundError(f"Task with id {task_id} not found.")
        task.status = status
        session.add(task)
        await session.commit()
        await session.refresh(task)


async def upload_file(file: UploadFile, task_id: UUID) -> None:
    csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    csv_data = list()
    for row in csv_reader:
        csv_data.append(FileData(task_id=task_id,
                                 country=row["country"],
                                 latitude=row["latitude"],
                                 longitude=row["longitude"]))
    await bulk_create(csv_data)
    file.file.close()


async def get_all_coordinates_for_task(task_id: UUID) -> List[FileData]:
    async with scoped_session() as session:
        result = await session.execute(select(FileData).filter(FileData.task_id == task_id))
        file_data = result.scalars().all()
        return file_data


async def get_all_points_for_task(task_id: UUID) -> List[Point]:
    async with scoped_session() as session:
        result = await session.execute(select(Point).filter(Point.task_id == task_id))
        points = result.scalars().all()
        return points


async def get_all_links_for_task(task_id: UUID) -> List[Link]:
    async with scoped_session() as session:
        result = await session.execute(select(Link).filter(Link.task_id == task_id))
        link_data = result.scalars().all()
        return link_data
