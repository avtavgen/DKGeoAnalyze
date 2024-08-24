import uuid
from enum import auto, StrEnum
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


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
    task_id: uuid.UUID | None = Field(default=None, foreign_key="task.id")


class Point(ChildBase, table=True):
    address: str = Field(default="None", nullable=False)
    task: "Task" = Relationship(back_populates="points")


class Link(ChildBase, table=True):
    distance: str = Field(default="None", nullable=False)
    task: "Task" = Relationship(back_populates="links")


class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: StatusEnum = Field(default=StatusEnum.CREATED, nullable=False)
    points: Optional[List[Point]] = Relationship(back_populates="task",
                                                 sa_relationship_kwargs={"lazy": "joined"})
    links: Optional[List[Link]] = Relationship(back_populates="task",
                                               sa_relationship_kwargs={"lazy": "joined"})


class PointResponse(BaseModel):
    name: str
    address: str


class LinkResponse(BaseModel):
    name: str
    distance: str


class TaskResponse(BaseModel):
    id: uuid.UUID
    status: str


class TaskDataResponse(BaseModel):
    id: uuid.UUID
    status: str
    points: List[PointResponse] = []
    links: List[LinkResponse] = []
