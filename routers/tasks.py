from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from db.models import NotFoundError, DBTask
from db.tasks import create_db_task, read_db_task
from db.core import get_session

from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(
    prefix="/api",
)


@router.get("/create_task")
async def create_task(request: Request, session: AsyncSession = Depends(get_session)) -> DBTask:
    db_task = await create_db_task(session)
    return db_task


@router.get("/{task_id}")
async def read_item(request: Request, item_id: UUID, session: AsyncSession = Depends(get_session)) -> DBTask:
    try:
        db_task = await read_db_task(item_id, session)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_task
