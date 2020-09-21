import asyncio
import logging
import threading
from typing import List

import requests
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal, engine
from app.models import Resource, ResourceItem

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
templates = Jinja2Templates(directory='app/templates')

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
MAX_THREADS = 50

lock = threading.Lock()

if not logger.hasHandlers():
    sh = logging.StreamHandler()
    fmt = logging.Formatter(fmt="%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.propagate = False


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def download_url(url):
    try:
        resp = requests.get(f'http://{url}', timeout=30)
    except:
        resp = None
    return resp


def prepare_resources():
    db: Session = next(get_db(), None)
    resources = db.query(Resource).filter(Resource.done == False).limit(25)
    return ('find_resource_items', resources) if resources.count() else (None, None)


def prepare_resource_items():
    db: Session = next(get_db(), None)
    resource_items = db.query(ResourceItem).filter(ResourceItem.done == False).limit(25)
    return ('find_keywords', resource_items) if resource_items.count() else (None, None)


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


class TextArea(BaseModel):
    urls: str
    keywords: str


@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/add/')
async def home(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})


@app.get('/results/')
async def home(request: Request):
    return templates.TemplateResponse("results.html", {"request": request})


@app.delete("/api/tasks/delete/")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        db.delete(id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.get("/api/tasks/", response_model=List[schemas.Task])
async def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


@app.post('/api/tasks/add/')
async def add_task(data: TextArea, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    data = data.dict()

    urls = list(filter(len, data.get('urls').lower().splitlines()))  # drop blank lines
    keywords = list(filter(len, data.get('keywords').lower().splitlines()))  # drop blank lines

    task = schemas.TaskCreate(keywords=keywords)
    task = crud.create_task(db=db, task=task)

    for url in urls:
        resource = schemas.ResourceCreate(url=url)
        crud.create_resource(db=db, resource=resource, task_id=task.id)

    return {'task_id': task.id}


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(process())
