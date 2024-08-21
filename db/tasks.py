import codecs
import csv
from typing import List
from uuid import UUID

from fastapi import UploadFile
from sqlmodel import select

from db.core import scoped_session
from db.models import DBTask, NotFoundError, CSVData, Point, Link
from sqlmodel.ext.asyncio.session import AsyncSession


async def read_db_task(task_id: UUID, session: AsyncSession) -> DBTask:
    task = await session.get(DBTask, task_id)
    if task is None:
        raise NotFoundError(f"Task with id {task_id} not found.")
    return task


async def read_celery_task(task_id: UUID) -> DBTask:
    async with scoped_session() as session:
        task = await session.get(DBTask, task_id)
        if task is None:
            raise NotFoundError(f"Task with id {task_id} not found.")
        return task


async def create_db_task(session: AsyncSession) -> DBTask:
    task = DBTask()
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


async def update_task_status(task_id: UUID, status: str) -> None:
    async with scoped_session() as session:
        task = await session.get(DBTask, task_id)
        if task is None:
            raise NotFoundError(f"Task with id {task_id} not found.")
        task.status = status
        session.add(task)
        await session.commit()
        await session.refresh(task)


async def create_csv_data(session: AsyncSession, country: str, latitude: str, longitude: str, db_task: DBTask) -> None:
    csv_data = CSVData(task_id=db_task.id, country=country, latitude=latitude, longitude=longitude)
    session.add(csv_data)
    await session.commit()
    await session.refresh(csv_data)


async def create_point(name: str, address: str, task_id: UUID) -> None:
    async with scoped_session() as session:
        point = Point(name=name, address=address, task_id=task_id)
        session.add(point)
        await session.commit()
        await session.refresh(point)


async def create_link(name: str, distance: str, task_id: UUID) -> None:
    async with scoped_session() as session:
        link = Link(name=name, distance=distance, task_id=task_id)
        session.add(link)
        await session.commit()
        await session.refresh(link)


async def upload_file(file: UploadFile, session: AsyncSession, db_task: DBTask) -> None:
    csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    for row in csv_reader:
        await create_csv_data(session=session, country=row["country"], latitude=row["latitude"],
                              longitude=row["longitude"], db_task=db_task)
    file.file.close()


async def get_all_coordinates_for_task(task_id: UUID) -> List[CSVData]:
    async with scoped_session() as session:
        task = await session.get(DBTask, task_id)
        if task is None:
            raise NotFoundError(f"Task with id {task_id} not found.")
        result = await session.execute(select(CSVData).filter(CSVData.task_id == task.id))
        csv_data = result.scalars().all()
        return csv_data


async def get_all_points_for_task(task_id: UUID) -> List[Point]:
    async with scoped_session() as session:
        task = await session.get(DBTask, task_id)
        if task is None:
            raise NotFoundError(f"Task with id {task_id} not found.")
        result = await session.execute(select(Point).filter(Point.task_id == task.id))
        points = result.scalars().all()
        return points


async def get_all_links_for_task(task_id: UUID) -> List[Link]:
    async with scoped_session() as session:
        task = await session.get(DBTask, task_id)
        if task is None:
            raise NotFoundError(f"Task with id {task_id} not found.")
        result = await session.execute(select(Link).filter(Link.task_id == task.id))
        links = result.scalars().all()
        return links


async def update_task_data(task_id: UUID, links: List[Link], points: List[Point]) -> DBTask:
    async with scoped_session() as session:
        task = await session.get(DBTask, task_id)
        if task is None:
            raise NotFoundError(f"Task with id {task_id} not found.")
        task.links = links
        task.points = points
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task
