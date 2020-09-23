from pathlib import Path
from typing import Optional

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

from app.apps.keywords.models.pydantic.database import DatabaseURL

p: Path = Path(__file__).parents[1] / '.env'
config: Config = Config(p if p.exists() else None)


##########################################################################
# DataBase settings
##########################################################################

DB_NAME: str = config('DB_NAME', cast=str)
DB_USER: Optional[str] = config('DB_USER', cast=str, default=None)
DB_PASSWORD: Optional[Secret] = config('DB_PASSWORD', cast=Secret, default=None)
DB_HOST: str = config('DB_HOST', cast=str, default='localhost')
DB_PORT: int = config('DB_PORT', cast=int, default=5432)

DATABASE_CONFIG: DatabaseURL = DatabaseURL(
    drivername='asyncpg',
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

ALEMBIC_CONFIG: DatabaseURL = DatabaseURL(
    drivername='postgresql+psycopg2',
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

# DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADRESS}/{DB_NAME}"

REDIS_IP: str = config('REDIS_IP', cast=str, default='127.0.0.1')
REDIS_PORT: int = config('REDIS_PORT', cast=int, default=6379)

SENTRY_DSN: Optional[Secret] = config('SENTRY_DSN', cast=Secret, default=None)

ARQ_BACKGROUND_FUNCTIONS: Optional[CommaSeparatedStrings] = config('ARQ_BACKGROUND_FUNCTIONS',
                                                                   cast=CommaSeparatedStrings,
                                                                   default=None)

##########################################################################
# Server settings
##########################################################################

SERVER_ADRESS = '0.0.0.0'
SERVER_PORT = 8080
SERVER_LOG_LEVEL = 'debug'
SERVER_WORKER_NUMBERS = 1

##########################################################################
# Log settings
##########################################################################

# replicate the dictConfig logging in uvicorn and update the existing formatter.
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(name)s - %(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s - %(name)s - %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}
