import logging

from gino.ext.starlette import Gino

from app.core.config import DATABASE_CONFIG

LOGGER = logging.getLogger(__name__)

LOGGER.info(f"Initialise Gino engine and connecting to {DATABASE_CONFIG.url}")
db = Gino(dsn=DATABASE_CONFIG.url)
