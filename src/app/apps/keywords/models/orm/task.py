import datetime
from typing import List

from sqlalchemy.orm import relationship

from app.apps.keywords.models.pydantic.task import TaskCreateSchema, TaskUpdateSchema
from app.core.db import db


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    keywords = db.Column(db.ARRAY(db.String))
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    resources = relationship('Resource', back_populates='task')


class TaskQueries:
    async def create_task(self, task: TaskCreateSchema) -> Task:
        return await Task.create(**task.__dict__)

    async def update_task(self, old_task: Task, new_task: TaskUpdateSchema) -> Task:
        task_updated = await old_task.update(**new_task.__dict__).apply()
        return task_updated._instance

    async def delete_task(self, task_id: int) -> Task:
        return await Task.get(task_id).delete()

    async def get_task_by_id(self, task_id: int) -> Task:
        return await Task.get(task_id)

    async def get_all_tasks(self) -> List[Task]:
        return await Task.query.gino.all()
