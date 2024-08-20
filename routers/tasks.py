from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from db.models import NotFoundError
from db.tasks import Task, create_db_task, read_db_task

router = APIRouter(
    prefix="/api",
)


@router.get("/create_task")
def create_task(request: Request) -> Task:
    db_task = create_db_task()
    return Task(**db_task.__dict__)


@router.get("/{task_id}")
def read_item(request: Request, item_id: UUID) -> Task:
    try:
        db_task = read_db_task(item_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return Task(**db_task.__dict__)
