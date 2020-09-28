import logging  # new
import os

from fastapi import FastAPI
from tortoise import Tortoise, run_async  # updated
from tortoise.contrib.fastapi import register_tortoise

log = logging.getLogger(__name__)  # new


# def init_db(app: FastAPI) -> None:
#     register_tortoise(
#         app,
#         db_url='postgres://keywords_finder:keywords_finder@postgres:5432/keywords_finder',
#         modules={"models": ["apps.keywords.models", "aerich.models"]},
#         generate_schemas=True,
#         add_exception_handlers=True,
#     )


async def generate_schema() -> None:
    log.info("Initializing Tortoise...")

    await Tortoise.init(
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["keywords.models", "aerich.models"]},
    )
    log.info("Generating database schema via Tortoise...")
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()


# new
if __name__ == "__main__":
    run_async(generate_schema())
