import uuid
from sqlmodel import SQLModel, Field
from enum import auto, StrEnum


class StatusEnum(StrEnum):
    CREATED = auto()
    RUNNING = auto()
    FAILED = auto()


class NotFoundError(Exception):
    pass


class DBTask(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: StatusEnum = Field(default=StatusEnum.CREATED, nullable=False)
