from uuid import UUID

from db.models import DBTask, NotFoundError
from sqlmodel.ext.asyncio.session import AsyncSession


async def read_db_task(task_id: UUID, session: AsyncSession) -> DBTask:
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
