from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from db.core import NotFoundError, get_db
from db.tasks import Task

router = APIRouter(
    prefix="/api",
)


@router.get("/getResult")
def get_task(request: Request, task_id: int, db: Session = Depends(get_db)) -> Task:
    # try:
    #     db_item = read_db_item(item_id, db)
    # except NotFoundError as e:
    #     raise HTTPException(status_code=404) from e
    return Task(id=1, status="running")
