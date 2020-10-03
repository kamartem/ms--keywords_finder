import logging
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, ValidationError
from pyexcelerate import Workbook
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.keywords.models import Resource, ResourceItem
from app.keywords.models.resource import Resource_Pydantic
from app.keywords.models.resource_item import ResourceItem_Pydantic
from app.keywords.models.task import Task, Task_Pydantic
from app.keywords.serializers.form import TextAreaTask

router = APIRouter()
LOG = logging.getLogger(__name__)


class Status(BaseModel):
    message: str


def background_on_message(task):
    LOG.error(task.id)


@router.get('/', response_model=List[Task_Pydantic])
async def list_tasks():
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
            url = f'http://{url}' if 'http' not in url else url
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


@router.get('/report/', response_class=StreamingResponse)
async def report(task_id: int):
    task = await Task.filter(id=task_id).first()
    resources = await Resource_Pydantic.from_queryset(Resource.filter(task_id=task.id))
    result = [['Ссылка', 'Найденные ключевые слова', 'Были ли проблемы']]

    for resource in resources:
        keywords = []
        problem = resource.had_error
        resource_items = await ResourceItem_Pydantic.from_queryset(ResourceItem.filter(resource_id=resource.id))
        for resource_item in resource_items:
            keywords.extend(resource_item.keywords_found)
            problem = problem or resource_item.had_error
        result.append([resource.url, ', '.join(str(s) for s in set(keywords)), 'Да' if problem else 'Нет'])

    wb = Workbook()
    wb.new_sheet("sheet name", data=result)
    wb.save('/tmp/result.xlsx')
    return FileResponse('/tmp/result.xlsx')
