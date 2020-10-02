import asyncio
import logging

import aiohttp

from app.keywords.models.resource import Resource, Resource_Pydantic
from app.keywords.models.resource_item import ResourceItem

LOG = logging.getLogger(__name__)


async def find_resource_items(resource_id):
    resource_obj =  await Resource.get(id=resource_id)
    resource_obj.done = True
    await resource_obj.save()


async def find_keywords(resource_item_id):
    resource_item_obj = await ResourceItem.get(id=resource_item_id)
    resource_item_obj.done = True
    await resource_item_obj.save()


def call_method(class_name, method_name, *params):
    return getattr(class_name, method_name)(*params)


async def fetch(session, url):
    async with session.get(url) as response:
        return await response


async def process(loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        while True:
            tasks_count = len(asyncio.all_tasks())

            if tasks_count <= 5:
                resources = await Resource_Pydantic.from_queryset(Resource.filter(done=False).limit(10))
                for resource in resources:
                    await loop.create_task(find_resource_items(resource.id))

            tasks_count = len(asyncio.all_tasks())
            if tasks_count <= 5:
                resource_items = await Resource_Pydantic.from_queryset(ResourceItem.filter(done=False).limit(30))
                for resource_item in resource_items:
                    await loop.create_task(find_keywords(resource_item.id))
            tasks_count = len(asyncio.all_tasks())

            sleep_time = 60 if tasks_count == 0 else 5
            LOG.error(f"Speeping for {sleep_time}")
            await asyncio.sleep(sleep_time)
