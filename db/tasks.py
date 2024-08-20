from typing import Optional, Type
from uuid import UUID, uuid4

from pydantic import BaseModel

from db.models import StatusEnum, DBTask, NotFoundError
from fastapi_sqlalchemy import db


class Task(BaseModel):
    id: UUID
    status: StatusEnum


def read_db_task(task_id: UUID) -> Type[DBTask]:
    db_task = db.session.query(DBTask).filter(DBTask.id == task_id).first()
    if db_task is None:
        raise NotFoundError(f"Task with id {task_id} not found.")
    return db_task


def create_db_task() -> DBTask:
    db_task = DBTask(id=uuid4(), status=StatusEnum.CREATED)
    db.session.add(db_task)
    db.session.commit()
    db.session.refresh(db_task)

    return db_task
