import logging
from typing import List

from fastapi import BackgroundTasks, Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory='app/templates')

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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


class TextArea(BaseModel):
    urls: str
    keywords: str


@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def background_task():
    logger.info('test')


@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


@app.post('/tasks/add/')
async def add_task(data: TextArea, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    data = data.dict()

    urls = list(filter(len, data.get('urls').lower().splitlines()))  # drop blank lines
    keywords = list(filter(len, data.get('keywords').lower().splitlines()))  # drop blank lines

    task = schemas.TaskCreate(keywords=keywords)
    task = crud.create_task(db=db, task=task)

    for url in urls:
        resource = schemas.ResourceCreate(url=url)
        crud.create_resource(db=db, resource=resource, task_id=task.id)

    background_tasks.add_task(background_task)

    return {'task_id': task.id}
