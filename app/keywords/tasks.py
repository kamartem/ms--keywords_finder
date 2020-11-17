import asyncio
from collections import Counter
from urllib.parse import urlparse

import aiohttp
import async_timeout
from aiologger import Logger
from aiologger.levels import LogLevel
from bs4 import BeautifulSoup
from tortoise.query_utils import Q

from app.keywords.models import Resource, ResourceItem

LOG = Logger.with_default_handlers(level=LogLevel.INFO)
# LOG = logging.getLogger(__name__)

BAD_EXTENSIONS = ['jpg', 'png', 'jpeg', 'gif', 'svg', 'css', 'js', 'xml', 'ico', 'xls', 'xlsx']
BAD_EXTENSIONS = [f'.{ext}' for ext in BAD_EXTENSIONS]

USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'


async def fetch(session, url):
    error, data = False, None
    LOG.info(f"Try fetch {url}")

    try:
        with async_timeout.timeout(5):

            async with session.get(url, verify_ssl=False) as response:
                if response.status != 200:
                    error = f"Status: {response.status}, reason: {response.reason}"
                else:
                    try:
                        LOG.info(f"Got response {url}")
                        data = await response.text(errors='replace')
                    except Exception as e:
                        error = f"An unicode error: {e}"
    except asyncio.TimeoutError as e:
        error = f"Timeout"
    except Exception as e:
        error = f"Possible HTTP/SSL errors {e}"

    if error:
        LOG.info(f"Eror on getting :{url} {error}")

    return error, data


async def bound_fetch(url, sem, session):
    # Getter function with semaphore.
    async with sem:
        return await fetch(session, url)


async def process_resource_item_content(resource_item_obj, keywords_to_found, error, content):
    if error:
        resource_item_obj.error = error
    else:
        content_lower = content.lower()
        kwds = [kw for kw in keywords_to_found if kw.lower() in content_lower]
        if len(kwds) > 0:
            resource_item_obj.keywords_found = kwds

    resource_item_obj.done = True
    await resource_item_obj.save()


async def process_resource(resource_obj, sem, session):
    scheme = 'http' if resource_obj.done_https else 'https'
    resource_url = f'{scheme}://{resource_obj.domain}'

    error, content = await bound_fetch(resource_obj.get_current_url(), sem, session)
    if error:
        if scheme == 'https':
            resource_obj.error_https = error
        else:
            resource_obj.error_http = error
    else:
        result = []
        soup = BeautifulSoup(content, features="html.parser")
        links = [a.get('href') for a in soup.find_all('a', href=True)]

        for link in links:
            if link.startswith('/'):
                result.append(f'{resource_url}{link}')
            else:
                parsed = urlparse(link)
                if resource_obj.domain == parsed.netloc and all(x not in link[-20:].lower() for x in BAD_EXTENSIONS):
                    proto = parsed.scheme if parsed.scheme else scheme
                    if proto in ('http', 'https'):
                        result.append(f'{proto}://{parsed.netloc}{parsed.path}')
        c = Counter(result)
        data = set([url[0] for url in c.most_common(5)])
        if resource_url not in data and f'{resource_url}/' not in data:
            data.add(resource_url)

        for el in data:
            try:
                resource_item = await ResourceItem.create(resource_id=resource_obj.id, url=el)
                if el in [resource_url, f'{resource_url}/']:
                    task = await resource_obj.task
                    LOG.info(task)
                    LOG.info(task.keywords)
                    await process_resource_item_content(resource_item, task.keywords, None, content)
            except Exception as e:
                LOG.error(e)

        resource_obj.done = True

    if scheme == 'https':
        resource_obj.done_https = True
    else:
        resource_obj.done_http = True

    if resource_obj.done_https and resource_obj.done_http and resource_obj.error_https and resource_obj.error_http:
        await ResourceItem.create(resource_id=resource_obj.id, url=resource_url, done=True)
        resource_obj.done = True

    await resource_obj.save()


async def process_resource_item(resource_item_obj, sem, session):
    resource = await resource_item_obj.resource
    task = await resource.task
    error, content = await bound_fetch(resource_item_obj.url, sem, session)
    await process_resource_item_content(resource_item_obj, task.keywords, error, content)


async def process():
    sem = asyncio.Semaphore(5)
    connector = aiohttp.TCPConnector(verify_ssl=False)

    async with aiohttp.ClientSession(headers={'User-Agent': USER_AGENT}, connector=connector) as session:
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
            else:
                await asyncio.sleep(5)
