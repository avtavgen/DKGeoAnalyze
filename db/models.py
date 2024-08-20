from enum import Enum, auto
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class StatusEnum(Enum):
    CREATED = auto()
    RUNNING = auto()
    FAILED = auto()


class NotFoundError(Exception):
    pass


class Base(DeclarativeBase):
    pass


class DBTask(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    status: Mapped[StatusEnum]
