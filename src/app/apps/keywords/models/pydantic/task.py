from typing import List

from pydantic import BaseModel


class TaskBaseSchema(BaseModel):
    keywords: List[str] = None


class TaskCreateSchema(TaskBaseSchema):
    pass


class TaskUpdateSchema(TaskBaseSchema):
    pass


class TaskDBSchema(TaskBaseSchema):
    id: int
    resources: List

    class Config:
        orm_mode = True
