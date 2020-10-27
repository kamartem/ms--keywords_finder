import asyncio
from collections import Counter
from urllib.parse import urlparse

import aiohttp
import async_timeout
from aiologger import Logger
from aiologger.levels import LogLevel
from bs4 import BeautifulSoup
from tortoise.query_utils import Q

from app.keywords.models import Resource, ResourceItem, ResourceItem_Pydantic, Resource_Pydantic

LOG = Logger.with_default_handlers(level=LogLevel.ERROR)

BAD_EXTENSIONS = ['jpg', 'png', 'jpeg', 'gif', 'svg', 'css', 'js', 'xml', 'ico', 'xls', 'xlsx']
BAD_EXTENSIONS = [f'.{ext}' for ext in BAD_EXTENSIONS]

USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'


async def fetch(session, url):
    await LOG.info(f"Try fetch {url}")

    try:
        with async_timeout.timeout(5):
            async with session.get(url) as response:
                if response.status != 200:
                    await LOG.error(f"Error on getting {url}: status: {response.status}, reason: {response.reason}")
                    return
                else:
                    try:
                        text = await response.text(errors='replace')
                    except Exception as e:
                        await LOG.error(f"Error on getting {url}: an unicode error: {e}")
                        return e
                    LOG.info(f"Success on getting {url}")
                    return text

    except Exception as e:
        await LOG.error(f'Error on getting {url}: possible HTTP/SSL errors {e}')
        return e


async def bound_fetch(url, sem, session):
    # Getter function with semaphore.
    async with sem:
        return await fetch(session, url)


async def process_resource(resource_obj, sem, session):
    resource_pyd = Resource_Pydantic.from_tortoise_orm(resource_obj)
    scheme = 'http' if resource_pyd.done_https else 'https'
    resource_url = f'{scheme}://{resource_pyd.domain}'

    try:
        content = await bound_fetch(resource_pyd.get_current_url(), sem, session)
        result = []
        soup = BeautifulSoup(content, features="html5lib")
        links = [a.get('href') for a in soup.find_all('a', href=True)]

        for link in links:
            parsed = urlparse(link)
            if resource_pyd.domain == parsed.netloc and all(x not in link[-20:] for x in BAD_EXTENSIONS):
                proto = parsed.scheme if parsed.scheme else scheme
                result.append(f'{proto}://{parsed.netloc}{parsed.path}')
        c = Counter(result)
        data = list(set([url[0] for url in c.most_common(5)]))
        data.append(resource_url)

        for el in data:
            await ResourceItem.create(resource_id=resource_pyd.id, url=el)

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


async def process_resource_item(resource_item_obj, sem, session):
    resource_item_pyd = await ResourceItem_Pydantic.from_tortoise_orm(resource_item_obj)
    resource = resource_item_pyd.resource
    task = resource.task
    keywords_to_found = task.keywords

    content = await bound_fetch(resource_item_pyd.url, sem, session)
    if isinstance(content, Exception) or content is None:
        resource_item_obj.error = 'error'
    else:
        kwds = [kw for kw in keywords_to_found if kw.lower() in content.lower()]
        if len(kwds) > 0:
            resource_item_obj.keywords_found = kwds

    resource_item_obj.done = True
    await resource_item_obj.save()


async def process(loop):
    sem = asyncio.Semaphore(100)

    connector = aiohttp.TCPConnector(verify_ssl=False, keepalive_timeout=5.0)
    async with aiohttp.ClientSession(loop=loop, headers={'User-Agent': USER_AGENT}, connector=connector) as session:
        while True:
            tasks = []

            resources_qs = Resource.filter(
                Q(done_http=False) & Q(done_https=False)
                | Q(Q(done_https=True), Q(error_https__isnull=False), Q(done_http=False), join_type='AND')
                | Q(Q(done_http=True), Q(error_http__isnull=False), Q(done_https=False), join_type='AND')).limit(100)

            resources = await resources_qs
            resources_count = await resources_qs.count()

            LOG.info(f"Got {resources_count} resources")

            if resources_count > 0:
                for resource in resources:
                    task = asyncio.ensure_future(process_resource(resource, sem, session))
                    tasks.append(task)
            else:
                resource_items_qs = ResourceItem.filter(done=False).limit(100)
                resource_items = await resource_items_qs
                resources_items_count = await resource_items_qs.count()
                LOG.info(f"Got {resources_items_count} resource items")

                for resource_item in resource_items:
                    task = asyncio.ensure_future(process_resource_item(resource_item, sem, session))
                    tasks.append(task)

            if tasks:
                responses = asyncio.gather(*tasks)
                await responses
