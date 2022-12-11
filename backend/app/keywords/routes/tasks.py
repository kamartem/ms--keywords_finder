import itertools
import logging
from itertools import groupby
from operator import itemgetter
from typing import List
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, ValidationError
from pyexcelerate import Workbook
from tortoise.contrib.fastapi import HTTPNotFoundError

from app.keywords.models import Resource, ResourceItem, Task, Task_Pydantic
from app.keywords.serializers.form import TextAreaTask

router = APIRouter()
LOG = logging.getLogger(__name__)


class Status(BaseModel):
    message: str


@router.get("/", response_model=List[Task_Pydantic])
async def list_tasks():
    return await Task_Pydantic.from_queryset(Task.all())


@router.get(
    "/{task_id}",
    response_model=Task_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_task_by_id(task_id: int):
    return await Task_Pydantic.from_queryset_single(Task.get(id=task_id))


@router.post("/", response_model=Task_Pydantic)
async def create_task(data: TextAreaTask):
    data = dict(data)
    urls_2d = [
        line.split() for line in data.pop("urls").lower().splitlines() if line
    ]  # multiple urls in one line
    urls = list(itertools.chain(*urls_2d))

    try:
        resources_to_create = []
        keywords = data["keywords"].lower().splitlines()
        keywords = [keyword for keyword in keywords if keyword]
        task_obj = await Task.create(keywords=keywords)

        for idx, url in enumerate(urls):
            if "//" not in url:
                url = f"https://{url}"
            parsed_uri = urlparse(url)
            resources_to_create.append(
                Resource(task=task_obj, domain=parsed_uri.netloc, order=idx)
            )

        await Resource.bulk_create(resources_to_create)

    except ValidationError as e:
        LOG.error(e)

    return await Task_Pydantic.from_tortoise_orm(task_obj)


@router.delete(
    "/{task_id}",
    response_model=Task_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def delete_task(task_id: int):
    deleted_count = await Task.filter(id=task_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {task_id} not found")
    return Status(message=f"Deleted task {task_id}")


@router.get("/report/", response_class=StreamingResponse)
async def report(task_id: int):
    task = await Task.filter(id=task_id).first()
    result = [["Ссылка", "Найденные ключевые слова", "Были ли проблемы"]]
    resource_items = (
        await ResourceItem.filter(resource__task_id=task.id)
        .order_by("resource__order")
        .values(
            "resource_id",
            "resource__domain",
            "resource__error_https",
            "resource__error_http",
            "keywords_found",
            "done",
            "error",
        )
    )
    resource_with_grouper = groupby(resource_items, itemgetter("resource_id"))

    for resource_id, items in resource_with_grouper:
        keywords = set()
        problems = set()
        domain = ""

        for item in items:
            for x in item["keywords_found"]:
                keywords.add(x)
            if item["resource__error_https"] and item["resource__error_http"]:
                problems.add(item["resource__error_https"])
                problems.add(item["resource__error_http"])
            domain = item["resource__domain"]
        problems.discard(None)
        result.append(
            [
                domain,
                ", ".join(str(s) for s in keywords),
                ", ".join(str(e) for e in problems) if problems else "Нет",
            ]
        )

    wb = Workbook()
    wb.new_sheet("sheet name", data=result)
    wb.save("/tmp/result.xlsx")
    return FileResponse("/tmp/result.xlsx")
