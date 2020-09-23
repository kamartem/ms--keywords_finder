from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends

import logging

from app.apps.keywords.models.pydantic.task import TaskCreateSchema, TaskDBSchema
from app.apps.keywords.models.service.task import TaskService
from app.apps.keywords.utils import get_task_services
from starlette import status

router = APIRouter()
LOG = logging.getLogger(__name__)


@router.post('/', response_model=TaskDBSchema)
async def create_task(task: TaskCreateSchema, task_service: TaskService = Depends(get_task_services)) -> TaskDBSchema:
    return await task_service.create_task(task)


@router.get('/', response_model=List[TaskDBSchema])
async def list_tasks(task_service: TaskService = Depends(get_task_services)) -> List[TaskDBSchema]:
    tasks: List[TaskDBSchema] = await task_service.list_users()
    return tasks


@router.get("/{task_id}", response_model=TaskDBSchema)
async def get_user_by_id(task_id: int, task_service: TaskService = Depends(get_task_services)) -> Optional[TaskDBSchema]:
    task = await task_service.get_user_by_id(task_id)
    if task:
        return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id:{task_id} not found",
    )

# @router.get('/', tags=["Tasks"], response_model=List[TaskDBSchema])
# async def read_tasks(skip: int = 0, limit: int = 100):
#     all_tasks = await ORMTask.query.gino.all()
#     return ORMTask.from_orm(all_tasks)


# @router.post('/', tags=["Tasks"], response_model=TaskSchema)
# async def create_task(data: TextArea):
#     LOG.info('123')
#     LOG.info(data)
#     # new_task: TaskCreate = await ORMTask.create(**data.dict())
#
#     # urls = list(filter(len, data.get('urls').lower().splitlines()))  # drop blank lines
#     # keywords = list(filter(len, data.get('keywords').lower().splitlines()))  # drop blank lines
#     #
#     # for url in urls:
#     #     resource = schemas.ResourceCreate(url=url)
#     #     crud.create_resource(db=db, resource=resource, task_id=task.id)
#
#     # return Task.from_orm(new_task)
#     return await ORMTask.get(1)


#
# @router.delete("/api/tasks/{id}/", tags=["Tasks"], response_model=Task)
# async def delete_task(task_id: int):
#     task: ORMTask = await ORMTask.get(id)
#     return await task.delete()
