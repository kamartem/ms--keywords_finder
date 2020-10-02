import logging
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError
from starlette.background import BackgroundTasks
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.keywords.models import Resource
from app.keywords.models.task import Task, Task_Pydantic
from app.keywords.serializers.form import TextAreaTask
from app.worker import celery_app

router = APIRouter()
LOG = logging.getLogger(__name__)


class Status(BaseModel):
    message: str


def background_on_message(task):
    LOG.error(task.id)


@router.get('/', response_model=List[Task_Pydantic])
async def list_tasks(background_task: BackgroundTasks):
    task = celery_app.send_task("app.keywords.tasks.test_celery", args=[123])
    background_task.add_task(background_on_message, task)
    return await Task_Pydantic.from_queryset(Task.all())


@router.get("/{task_id}", response_model=Task_Pydantic, responses={404: {"model": HTTPNotFoundError}})
async def get_task_by_id(task_id: int):
    return await Task_Pydantic.from_queryset_single(Task.get(id=task_id))


@router.post("/", response_model=Task_Pydantic)
async def create_task(data: TextAreaTask):
    data = dict(data)
    urls = data.pop('urls').lower().splitlines()

    try:
        keywords = data['keywords'].lower().splitlines()
        keywords = [keyword for keyword in keywords if keyword]
        task_obj = await Task.create(keywords=keywords)

        for url in urls:
            resource_obj = await Resource.create(task=task_obj, url=url)

    except ValidationError as e:
        print(e)

    return await Task_Pydantic.from_tortoise_orm(task_obj)


@router.delete("/{task_id}", response_model=Task_Pydantic, responses={404: {"model": HTTPNotFoundError}})
async def delete_user(task_id: int):
    deleted_count = await Task.filter(id=task_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {task_id} not found")
    return Status(message=f"Deleted task {task_id}")
