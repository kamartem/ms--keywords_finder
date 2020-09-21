import asyncio
import logging

from fastapi import FastAPI

from app.routes.tasks import router as task_router
from app.routes.html import router as html_router
from app.tasks import process

app = FastAPI()

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ROUTERS = (html_router, task_router)
for r in ROUTERS:
    app.include_router(r)

if not logger.hasHandlers():
    sh = logging.StreamHandler()
    fmt = logging.Formatter(fmt="%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.propagate = False


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(process())
