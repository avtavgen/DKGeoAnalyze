import uuid
from enum import auto, StrEnum
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class StatusEnum(StrEnum):
    CREATED = auto()
    RUNNING = auto()
    DONE = auto()
    FAILED = auto()


class NotFoundError(Exception):
    pass


class TableBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    task_id: uuid.UUID | None = Field(default=None, foreign_key="task.id")


class FileData(TableBase, table=True):
    country: str = Field(default="None", nullable=False)
    latitude: str = Field(default="None", nullable=False)
    longitude: str = Field(default="None", nullable=False)


class ChildBase(TableBase):
    name: str = Field(default="None", nullable=False)


class Point(ChildBase, table=True):
    address: str = Field(default="None", nullable=False)


class Link(ChildBase, table=True):
    distance: str = Field(default="None", nullable=False)


class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: StatusEnum = Field(default=StatusEnum.CREATED, nullable=False)


class PointResponse(BaseModel):
    name: str
    address: str


class LinkResponse(BaseModel):
    name: str
    distance: str


class TaskResponse(BaseModel):
    id: uuid.UUID
    status: str
    points: Optional[List[Point]] = None
    links: Optional[List[Link]] = None
