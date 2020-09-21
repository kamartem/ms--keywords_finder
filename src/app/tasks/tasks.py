import asyncio
import logging
import threading

import requests
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
# from app.models import Resource, ResourceItem
from app.routes.tasks import router as task_router

app = FastAPI()
templates = Jinja2Templates(directory='app/templates')

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

lock = threading.Lock()
def download_url(url):
    try:
        resp = requests.get(f'http://{url}', timeout=30)
    except:
        resp = None
    return resp


def prepare_resources():
    pass
#     db: Session = next(get_db(), None)
#     resources = db.query(Resource).filter(Resource.done == False).limit(25)
#     return ('find_resource_items', resources) if resources.count() else (None, None)
#
#
def prepare_resource_items():
    pass
#     db: Session = next(get_db(), None)
#     resource_items = db.query(ResourceItem).filter(ResourceItem.done == False).limit(25)
#     return ('find_keywords', resource_items) if resource_items.count() else (None, None)


class Scrapper:
    def find_resource_items(self, resource_id: int):
        db = SessionLocal()
        db.begin()
        x = db.query(Resource).get(resource_id)
        x.done = True
        db.commit()
        db.close()

    def find_keywords(self, resource_item_id: int):
        db = SessionLocal()
        db.begin()
        # content = download_url(resource_item.url)
        resource_item = db.query(ResourceItem).get(resource_item_id)
        resource_item.done = True
        db.commit()
        db.close()


def call_method(class_name, method_name, *params):
    return getattr(class_name, method_name)(*params)


async def process():
    while True:
        (func_name, items) = prepare_resources() or prepare_resource_items() or (None, [])
        items_count = items.count() if items else 0
        if items_count:
            if threading.active_count() <= 25:
                for item in items:
                    with lock:
                        t = threading.Thread(target=call_method, args=(Scrapper(), func_name, item))
                        t.start()
            else:
                logger.info("small sleep")
                await asyncio.sleep(60)
        else:
            logger.info("big sleep")
            await asyncio.sleep(5)
