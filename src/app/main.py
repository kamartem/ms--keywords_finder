from typing import Optional
from fastapi import FastAPI,Depends, File, Form, UploadFile, Request, HTTPException

from fastapi.templating import Jinja2Templates

from app import crud, models, schemas
from app.database import SessionLocal, engine

from sqlalchemy.orm import Session

from pydantic import BaseModel
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory='app/templates')

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


@app.post('/tasks/add')
async def add_task(data: TextArea, db: Session = Depends(get_db)):
    data = data.dict()

    urls = data.get('urls').lower().splitlines()
    keywords = data.get('keywords').lower().splitlines()

    task = schemas.TaskCreate(keywords=keywords)
    task = crud.create_task(db=db, task=task)

    for url in urls:
        resource = schemas.ResourceCreate(url=url)
        crud.create_resource(db=db, resource=resource, task_id=task.id)

    return {'task_id': task.id}
