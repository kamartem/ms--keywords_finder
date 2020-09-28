import logging
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError

from keywords.models.task import Task, Task_Pydantic

router = APIRouter()
LOG = logging.getLogger(__name__)


class Status(BaseModel):
    message: str


@router.get('/', response_model=List[Task_Pydantic])
async def list_tasks():
    return await Task_Pydantic.from_queryset(Task.all())


@router.get("/{task_id}", response_model=Task_Pydantic, responses={404: {"model": HTTPNotFoundError}})
async def get_task_by_id(task_id: int):
    return await Task_Pydantic.from_queryset_single(Task.get(id=task_id))


@router.post("/", response_model=Task_Pydantic)
async def create_task(task: Task_Pydantic):
    task_obj = await Task.create(**task.dict(exclude_unset=True))
    return await Task_Pydantic.from_tortoise_orm(task_obj)


@router.delete("/{task_id}", response_model=Task_Pydantic, responses={404: {"model": HTTPNotFoundError}})
async def delete_user(task_id: int):
    deleted_count = await Task.filter(id=task_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {task_id} not found")
    return Status(message=f"Deleted task {task_id}")
