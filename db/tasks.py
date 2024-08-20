from typing import Optional
from pydantic import BaseModel


class Task(BaseModel):
    id: int
    status: str
    data: Optional[str] = None
