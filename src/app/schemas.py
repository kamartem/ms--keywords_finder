from typing import List, Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    keywords: List[str] = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True


class ResourceBase(BaseModel):
    url: str
    done: bool


class ResourceCreate(ResourceBase):
    pass


class Resource(ResourceBase):
    id: int
    keywords_found: List[str] = []

    class Config:
        orm_mode = True