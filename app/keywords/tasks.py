import asyncio
import logging
from collections import Counter
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup
from tortoise.query_utils import Q

from app.keywords.models import Resource, ResourceItem, ResourceItem_Pydantic, Resource_Pydantic

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
BAD_EXTENSIONS = ['jpg', 'png', 'jpeg', 'gif', 'svg', 'css', 'js', 'xml', 'ico', 'xls', 'xlsx']
BAD_EXTENSIONS = [f'.{ext}' for ext in BAD_EXTENSIONS]


async def get_resource_items(session, resource_id, count=5):
    resource_qs = Resource.filter(id=resource_id).first()
    resource_obj = await resource_qs
    resource_pyd = await Resource_Pydantic.from_queryset_single(resource_qs)
    scheme = 'http' if resource_pyd.done_https else 'https'
    resource_url = f'{scheme}://{resource_pyd.domain}'

    try:
        async with session.get(resource_url) as ans:
            content = await ans.text(errors='replace')
            result = []
            soup = BeautifulSoup(content, features="lxml")
            links = [a.get('href') for a in soup.find_all('a', href=True)]

            for link in links:
                parsed = urlparse(link)
                if resource_pyd.domain == parsed.netloc and all(x not in link[-20:] for x in BAD_EXTENSIONS):
                    proto = parsed.scheme if parsed.scheme else scheme
                    result.append(f'{proto}://{parsed.netloc}{parsed.path}')
            c = Counter(result)
            data = list(set([url[0] for url in c.most_common(count)]))
            data.append(resource_url)

            for el in data:
                await ResourceItem.create(resource_id=resource_id, url=el)

    except Exception as e:
        if scheme == 'https':
            resource_obj.error_https = e
        else:
            resource_obj.error_http = e

    if scheme == 'https':
        resource_obj.done_https = True
    else:
        resource_obj.done_http = True

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
            content = (await ans.text(errors='replace')).lower()
            kwds = [kw for kw in keywords_to_found if kw.lower() in content]
            if len(kwds) > 0:
                resource_item_obj.keywords_found = kwds

    except Exception as e:
        resource_item_obj.error = e

    resource_item_obj.done = True
    await resource_item_obj.save()


async def process(loop):
    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(headers={'Connection': 'keep-alive'},
                                     timeout=timeout,
                                     connector=aiohttp.TCPConnector(verify_ssl=False),
                                     loop=loop) as session:
        while True:
            tasks_count = len(asyncio.all_tasks())
            if tasks_count <= 30:
                qs = Resource.filter(
                    Q(done_http=False) & Q(done_https=False)
                    | Q(Q(done_https=True), Q(error_https__isnull=False), Q(done_http=False), join_type='AND')
                    | Q(Q(done_http=True), Q(error_http__isnull=False), Q(done_https=False), join_type='AND'))
                resources = await Resource_Pydantic.from_queryset(qs.limit(20))
                for resource in resources:
                    await loop.create_task(get_resource_items(session, resource.id))
            tasks_count = len(asyncio.all_tasks())
            if tasks_count <= 30:
                resource_items = await ResourceItem_Pydantic.from_queryset(ResourceItem.filter(done=False).limit(20))
                for resource_item in resource_items:
                    await loop.create_task(find_keywords(session, resource_item.id))

            tasks_count = len(asyncio.all_tasks())
            if tasks_count <= 3:
                sleep_time = 30
            elif tasks_count <= 8:
                sleep_time = 15
            elif tasks_count <= 10:
                sleep_time = 10
            elif tasks_count <= 30:
                sleep_time = 5
            else:
                sleep_time = 10

            await asyncio.sleep(sleep_time)
