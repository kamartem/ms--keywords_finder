import asyncio
import logging
from collections import Counter
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from app.keywords.models.resource import Resource, Resource_Pydantic
from app.keywords.models.resource_item import ResourceItem, ResourceItem_Pydantic

LOG = logging.getLogger(__name__)


async def get_resource_items(session, resource_id, count=5):
    resource_qs = Resource.filter(id=resource_id).first()
    resource_obj = await resource_qs
    resource_ped = await Resource_Pydantic.from_queryset_single(resource_qs)
    parsed_uri = urlparse(resource_ped.url)
    domain = parsed_uri.netloc

    try:
        async with session.get(f'http://{domain}') as ans:
            content = await ans.text()

            soup = BeautifulSoup(content, features="lxml")
            hrefs = [
                f'http://{domain}{link["href"] if link["href"].startswith("/") else "/" + link["href"]}'
                for link in soup.find_all(
                    "a", href=lambda x: x and not x.startswith('http') and ':' not in x and not x.startswith('#'))
            ]
            hrefs2 = [
                link["href"] for link in soup.find_all("a", href=lambda x: x and domain in x and 'mailto' not in x)
            ]
            result = [f'http://{domain}'] + hrefs + hrefs2
            c = Counter(result)
            data = list(set([domain[0] for domain in c.most_common(count)]))

            for el in data:
                await ResourceItem.create(resource_id=resource_id, url=el)

            resource_obj.had_error = False

    except Exception as e:
        resource_obj.had_error = True
        LOG.error(e)

    resource_obj.done = True
    await resource_obj.save()


async def find_keywords(session, resource_item_id):
    resource_item_qs = ResourceItem.filter(id=resource_item_id).first()
    resource_item_obj = await resource_item_qs
    resource_item_pyd = await ResourceItem_Pydantic.from_queryset_single(resource_item_qs)
    resource = resource_item_pyd.resource
    task = resource.task
    keywords_to_found = task.keywords
    url = resource_item_pyd.url

    try:
        async with session.get(url) as ans:
            content = await ans.text()
            kwds = [kw for kw in keywords_to_found if kw in content]
            if len(kwds) > 0:
                resource_item_obj.keywords_found = kwds
            resource_item_obj.had_error = False
    except Exception as e:
        resource_item_obj.had_error = True
        LOG.error(e)

    resource_item_obj.done = True
    await resource_item_obj.save()


def call_method(class_name, method_name, *params):
    return getattr(class_name, method_name)(*params)


async def process(loop):
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(verify_ssl=False),
                                     loop=loop) as session:
        while True:
            tasks_count = len(asyncio.all_tasks())

            if tasks_count <= 30:
                resources = await Resource_Pydantic.from_queryset(Resource.filter(done=False).limit(30))
                for resource in resources:
                    await loop.create_task(get_resource_items(session, resource.id))
            tasks_count = len(asyncio.all_tasks())
            if tasks_count <= 30:
                resource_items = await ResourceItem_Pydantic.from_queryset(ResourceItem.filter(done=False).limit(40))
                for resource_item in resource_items:
                    await loop.create_task(find_keywords(session, resource_item.id))

            tasks_count = len(asyncio.all_tasks())
            if tasks_count <= 3:
                sleep_time = 10
            elif tasks_count <= 10:
                sleep_time = 15
            elif tasks_count <= 30:
                sleep_time = 5
            else:
                sleep_time = 3

            LOG.error(f"Sleeping for {sleep_time}")
            await asyncio.sleep(sleep_time)
