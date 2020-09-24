from typing import Any, List, Optional

from app.apps.keywords.models.pydantic.task import TaskCreateSchema, TaskDBSchema, TaskUpdateSchema


class TaskService:
    def __init__(self, task_queries: Any):
        self.__task_queries = task_queries

    async def create_task(self, task: TaskCreateSchema) -> TaskDBSchema:
        new_task = await self.__task_queries.create_task(task)
        return TaskDBSchema.from_orm(new_task)

    async def list_tasks(self) -> List[TaskDBSchema]:
        tasks = await self.__task_queries.get_all_tasks()
        tasks_schema = list(map(lambda x: TaskDBSchema.from_orm(x), tasks))
        return tasks_schema

    async def get_task_by_id(self, task_id: int) -> Optional[TaskDBSchema]:
        task = await self.__task_queries.get_task_by_id(task_id)
        if task:
            return TaskDBSchema.from_orm(task)
        else:
            return None

    async def update_task(self, task_id: int, new_task: TaskUpdateSchema) -> TaskDBSchema:
        old_task = await self.__task_queries.get_task_by_id(task_id)
        task_updated = await self.__task_queries.update_task(old_task, new_task)
        return TaskDBSchema.from_orm(task_updated)

    async def remove_task(self, task_id: int) -> TaskDBSchema:
        task_removed = await self.__task_queries.delete_task(task_id)
        return TaskDBSchema.from_orm(task_removed)
