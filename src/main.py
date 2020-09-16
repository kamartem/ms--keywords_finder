from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile, Request

from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory='templates')


class TextArea(BaseModel):
    urls: str
    keywords: str


@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post('/tasks/add')
async def add_task(data: TextArea):
    data = data.dict()

    domains = data.get('urls').lower().splitlines()
    keywords = data.get('keywords').lower().splitlines()

    task_id = 333

    return {'task_id': task_id}
