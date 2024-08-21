from uuid import UUID

from fastapi import File, APIRouter, HTTPException, Request, UploadFile
from fastapi.params import Depends

from db.models import NotFoundError, DBTask, StatusEnum
from db.tasks import create_db_task, read_db_task, upload_file, update_task_status, get_all_links_for_task, \
    get_all_points_for_task, update_task_data
from db.core import get_session
from service.celery_tasks import task_main

from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(
    prefix="/api",
)


@router.post("/calculateDistances")
async def post_upload_file(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)) -> DBTask:
    db_task = await create_db_task(session)
    await upload_file(file, session, db_task)
    await update_task_status(task_id=db_task.id, status=StatusEnum.RUNNING)
    task_main.delay(db_task_id=db_task.id)
    return db_task


@router.get("/getResult")
async def read_item(request: Request, item_id: UUID, session: AsyncSession = Depends(get_session)) -> DBTask:
    try:
        db_task = await read_db_task(item_id, session)
        if db_task.status == StatusEnum.DONE:
            lnk = await get_all_links_for_task(task_id=db_task.id)
            pnt = await get_all_points_for_task(task_id=db_task.id)
            await update_task_data(task_id=db_task.id, links=lnk, points=pnt)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_task
