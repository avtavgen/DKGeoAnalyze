import os
from asyncio import current_task
from contextlib import asynccontextmanager

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

async_engine = create_async_engine(
    os.environ.get("DATABASE_URL"),
    echo=True,
    future=True,
    poolclass=NullPool
)


@asynccontextmanager
async def scoped_session():
    scoped_factory = async_scoped_session(
        session_factory=sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False),
        scopefunc=current_task
    )
    try:
        async with scoped_factory() as s:
            yield s
    finally:
        await scoped_factory.remove()
