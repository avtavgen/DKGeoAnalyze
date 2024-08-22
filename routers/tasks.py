from uuid import UUID

from fastapi import File, APIRouter, HTTPException, UploadFile

from db.models import NotFoundError, StatusEnum, TaskResponse, PointResponse, LinkResponse
from db.tasks import get_or_create_task, upload_file, update_task_status, get_all_links_for_task, \
    get_all_points_for_task
from service.celery_tasks import task_main

router = APIRouter(
    prefix="/api",
)


@router.post("/calculateDistances")
async def post_upload_file(file: UploadFile = File(...)) -> TaskResponse:
    db_task = await get_or_create_task()
    await upload_file(file=file, task_id=db_task.id)
    await update_task_status(task_id=db_task.id, status=StatusEnum.RUNNING)
    task_main.delay(task_id=db_task.id)
    return TaskResponse(**db_task.__dict__)


@router.get("/getResult")
async def read_item(item_id: UUID) -> TaskResponse:
    try:
        task = await get_or_create_task(task_id=item_id)
        task_response = TaskResponse(**task.__dict__)
        if task_response.status == StatusEnum.DONE:
            all_links = await get_all_links_for_task(task_id=task_response.id)
            all_points = await get_all_points_for_task(task_id=task_response.id)
            task_response.points = [PointResponse(name=point.name, address=point.address) for point in all_points]
            task_response.links = [LinkResponse(name=link.name, distance=link.distance) for link in all_links]
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return task_response
