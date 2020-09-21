from typing import List

from pydantic import BaseModel


class TaskBase(BaseModel):
    keywords: List[str] = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    resources: List

    class Config:
        orm_mode = True
