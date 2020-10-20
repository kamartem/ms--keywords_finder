import itertools
import logging
from typing import List
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, ValidationError
from pyexcelerate import Workbook
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.keywords.models import Resource, ResourceItem, ResourceItem_Pydantic, Resource_Pydantic, Task, Task_Pydantic
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
    urls_2d = [line.split() for line in data.pop('urls').lower().splitlines() if line]  # multiple urls in one line
    urls = list(itertools.chain(*urls_2d))

    try:
        keywords = data['keywords'].lower().splitlines()
        keywords = [keyword for keyword in keywords if keyword]
        task_obj = await Task.create(keywords=keywords)
        LOG.error(task_obj)
        for url in urls:
            if '//' not in url:
                url = f'https://{url}'
            parsed_uri = urlparse(url)
            LOG.error(parsed_uri)
            resource_obj = await Resource.create(task=task_obj, domain=parsed_uri.netloc)

    except ValidationError as e:
        LOG.error(e)

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
