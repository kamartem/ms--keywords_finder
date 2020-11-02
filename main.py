import asyncio
import logging

import nest_asyncio
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import TORTOISE_ORM
from app.keywords.routes import keywords_router
from app.keywords.routes.html import router as html_router
from app.keywords.tasks import process

LOG = logging.getLogger(__name__)


def init_db(app: FastAPI):
    register_tortoise(app=app, config=TORTOISE_ORM)


def create_app() -> FastAPI:
    try:
        # if isinstance(SENTRY_DSN, Secret) and SENTRY_DSN.__str__() not in ("None", ""):
        #     initialize_sentry(dsn=SENTRY_DSN.__str__(), integrations=[SqlalchemyIntegration()])

        app: FastAPI = FastAPI()
        init_db(app)
        # init_admin(app=app) REF: https://github.com/maxim-petrov-fogstream/fastapi_rest_sceleton/blob/f0e2658a1fb669e45cb8cff888e250ae954f23cd/src/app.py
        ROUTERS = (html_router, keywords_router)
        for r in ROUTERS:
            app.include_router(r)
        # app.add_middleware( REF: https://github.com/maxim-petrov-fogstream/fastapi_rest_sceleton/blob/f0e2658a1fb669e45cb8cff888e250ae954f23cd/src/app.py
        #     CORSMiddleware,
        #     allow_origins=["*"],
        #     allow_credentials=True,
        #     allow_methods=["*"],
        #     allow_headers=["*"],
        # )
    except Exception as e:
        LOG.error(f"Error in fast-API app initialisation => {e}")
    return app


app = create_app()
nest_asyncio.apply()


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(process(loop))


@app.on_event("shutdown")
async def shutdown_event():
    LOG.info("Shutting down...")
