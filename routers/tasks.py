from uuid import UUID

from fastapi import File, APIRouter, HTTPException, UploadFile

from db.models import NotFoundError, StatusEnum, TaskResponse, TaskDataResponse
from db.tasks import get_or_create_task, upload_file, update_task_status
from service.celery_tasks import task_main

router = APIRouter(
    prefix="/api",
)


@router.post("/calculateDistances", response_model=TaskResponse)
async def post_upload_file(file: UploadFile = File(...)):
    task = await get_or_create_task()
    await upload_file(file=file, task_id=task.id)
    await update_task_status(task_id=task.id, status=StatusEnum.RUNNING)
    task_main.delay(task_id=task.id)
    return task


@router.get("/getResult", response_model=TaskDataResponse)
async def read_item(item_id: UUID):
    try:
        task = await get_or_create_task(task_id=item_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return task
