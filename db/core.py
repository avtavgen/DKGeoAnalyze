import os
from asyncio import current_task
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL = os.environ.get("DATABASE_URL")

async_engine = create_async_engine(
   DATABASE_URL,
   echo=True,
   future=True
)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


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
