from uuid import UUID

from fastapi import File, APIRouter, HTTPException, Request, UploadFile
from fastapi.params import Depends

from db.models import NotFoundError, DBTask
from db.tasks import create_db_task, read_db_task, upload_file
from db.core import get_session
from service.celery_tasks import task_main, TaskOut, _to_task_out

from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(
    prefix="/api",
)


@router.post("/calculateDistances")
async def post_upload_file(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)) -> TaskOut:
    db_task = await create_db_task(session)
    await upload_file(file, session, db_task)
    task = task_main.delay(db_task_id=db_task.id)
    return _to_task_out(task)


@router.get("/getResult/{task_id}")
async def read_item(request: Request, item_id: UUID, session: AsyncSession = Depends(get_session)) -> DBTask:
    try:
        db_task = await read_db_task(item_id, session)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_task
