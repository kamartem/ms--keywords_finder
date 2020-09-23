from app.apps.keywords.models.orm.task import TaskQueries
from app.apps.keywords.models.service.task import TaskService


def get_task_services() -> TaskService:
    return TaskService(TaskQueries())
