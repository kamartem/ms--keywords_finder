from typing import List

from fastapi import APIRouter

from app import crud
from app.models.orm.task import Task as ORMTask
from app.models.pydantic.form import TextArea
from app.models.pydantic.task import Task, TaskCreate

router = APIRouter()


@router.get("/api/tasks/", tags=["Tasks"], response_model=List[Task])
async def read_tasks(skip: int = 0, limit: int = 100):
    # tasks: ORMTask = await ORMTask.all()

    all_tasks = await ORMTask.query.gino.all()


    return ORMTask.from_orm(all_tasks)


# @router.post('/api/tasks/', tags=["Tasks"], response_model=Task)
# async def create_task(data: TextArea):
#     new_task: TaskCreate = await TaskCreate.create(**data.dict())
#
#     urls = list(filter(len, data.get('urls').lower().splitlines()))  # drop blank lines
#     keywords = list(filter(len, data.get('keywords').lower().splitlines()))  # drop blank lines
#     #
#     # for url in urls:
#     #     resource = schemas.ResourceCreate(url=url)
#     #     crud.create_resource(db=db, resource=resource, task_id=task.id)
#
#     return Task.from_orm(new_task)
#
#
# @router.delete("/api/tasks/{id}/", tags=["Tasks"], response_model=Task)
# async def delete_task(task_id: int):
#     task: ORMTask = await ORMTask.get(id)
#     return await task.delete()
