from typing import Any, List, Optional

from app.apps.keywords.models.pydantic.task import TaskCreateSchema, TaskDBSchema, TaskUpdateSchema


class TaskService:
    def __init__(self, task_queries: Any):
        self.__task_queries = task_queries

    async def create_task(self, task: TaskCreateSchema) -> TaskDBSchema:
        new_user = await self.__task_queries.create_task(task)
        return TaskDBSchema.from_orm(new_user)

    async def list_users(self) -> List[TaskDBSchema]:
        users = await self.__task_queries.get_all_users()
        users_schema = list(map(lambda x: TaskDBSchema.from_orm(x), users))
        return users_schema

    async def get_user_by_id(self, user_id: int) -> Optional[TaskDBSchema]:
        user = await self.__task_queries.get_user_byid(user_id)
        if user:
            return TaskDBSchema.from_orm(user)
        else:
            return None

    async def update_user(self, user_id: int, new_user: TaskUpdateSchema) -> TaskDBSchema:
        old_user = await self.__task_queries.get_user_byid(user_id)
        user_updated = await self.__task_queries.update_user(old_user, new_user)
        return TaskDBSchema.from_orm(user_updated)

    async def remove_user(self, user_id: int) -> TaskDBSchema:
        user_removed = await self.__task_queries.delete_user(user_id)
        return TaskDBSchema.from_orm(user_removed)
