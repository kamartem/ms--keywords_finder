import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from sentry_sdk import init as initialize_sentry
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from starlette.datastructures import Secret

from app.apps.keywords.routes import keywords_router
from app.apps.keywords.routes.html import router as html_router
from app.apps.keywords.tasks.tasks import process
from app.core.db import db
from app.core.config import DB_NAME, LOGGING_CONFIG, SENTRY_DSN, SERVER_ADRESS, SERVER_LOG_LEVEL, SERVER_PORT
from app.utils.sql import existing_database

LOGGER = logging.getLogger(__name__)


def create_app() -> FastAPI:
    try:
        if isinstance(SENTRY_DSN, Secret) and SENTRY_DSN.__str__() not in ("None", ""):
            initialize_sentry(dsn=SENTRY_DSN.__str__(), integrations=[SqlalchemyIntegration()])

        app: FastAPI = FastAPI(title="GINO FastAPI Keywords")
        db.init_app(app=app)
        ROUTERS = (html_router, keywords_router)
        for r in ROUTERS:
            app.include_router(r)
    except Exception as e:
        LOGGER.error(f"Error in fast-API app initialisation => {e}")
    return app


app: FastAPI = create_app()


@app.on_event("startup")
async def _startup() -> None:
    LOGGER.info("Check existing database")
    database: bool = await existing_database(db, DB_NAME)

    if not database:
        LOGGER.error(f"please create the required database before running the server db_name = {DB_NAME}")
    else:
        LOGGER.info("database checked")
        loop = asyncio.get_event_loop()
        loop.create_task(process())


def run() -> None:
    # os.system("uvicorn src.core.server:app --reload --lifespan on --workers 1 --host 0.0.0.0 --port 8080 --log-level debug")
    uvicorn.run(
        app,
        host=SERVER_ADRESS,
        port=SERVER_PORT,
        log_level=SERVER_LOG_LEVEL,
        log_config=LOGGING_CONFIG,
    )
