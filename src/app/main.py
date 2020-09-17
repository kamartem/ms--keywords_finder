import concurrent.futures
import logging
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
MAX_THREADS = 30

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
    logger.info(f"current url: {url}")
    resp = requests.get(f'http://{url}')
    return resp


def find_resource_items(resource_url):
    content = download_url(resource_url)


def find_keywords(url, keywords):
    content = download_url(url)


def process(urls):
    threads = min(MAX_THREADS, len(urls))

    if threads:
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(find_resource_items, urls)


def process2(urls):
    threads = min(MAX_THREADS, len(urls))

    if threads:
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(find_keywords, urls)


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


async def background_task(task_id: int):
    session = Session(engine)
    resources = session.query(Resource).filter(Resource.done == False, Resource.task_id == task_id)
    process([resource.url for resource in resources])

    logger.info("End find resource items")

    resource_items = session.query(ResourceItem).join(Resource).join(Resource.task).filter(ResourceItem.done == False,
                                                        Resource.task_id == task_id)
    process2([(resource_item.url, resource_item.task.keywords) for resource_item in resource_items])

    logger.info("End find keywords")


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

    background_tasks.add_task(background_task, task_id=task.id)

    return {'task_id': task.id}
