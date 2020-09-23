from fastapi import APIRouter

from app.apps.keywords.routes.tasks import router as tasks_router
from app.apps.keywords.routes.html import router as html_router

keywords_router = APIRouter()
keywords_router.include_router(html_router, prefix="")
keywords_router.include_router(tasks_router, prefix="/api/tasks", tags=["tesks"])
