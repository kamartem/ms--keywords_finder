from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory='app/templates')


@router.get('/')
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get('/add/')
async def home(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})


@router.get('/results/')
async def home(request: Request):
    return templates.TemplateResponse("results.html", {"request": request})
