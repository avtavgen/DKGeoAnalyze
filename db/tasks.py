import codecs
import csv
from uuid import UUID

from fastapi import UploadFile

from db.core import scoped_session
from db.models import DBTask, NotFoundError, CSVData
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


async def create_csv_data(session: AsyncSession, country: str, latitude: str, longitude: str, db_task: DBTask) -> None:
    csv_data = CSVData(task_id=db_task.id, country=country, latitude=latitude, longitude=longitude)
    session.add(csv_data)
    await session.commit()
    await session.refresh(csv_data)


async def upload_file(file: UploadFile, session: AsyncSession, db_task: DBTask) -> None:
    csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    for row in csvReader:
        await create_csv_data(session=session, country=row[0], latitude=row[1], longitude=row[2], db_task=db_task)

    file.file.close()
