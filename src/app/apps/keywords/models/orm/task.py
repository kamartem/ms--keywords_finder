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
    async def create_task(self, user: TaskCreateSchema) -> Task:
        return await Task.create(**user.__dict__)

    async def update_user(self, old_user: Task, new_user: TaskUpdateSchema) -> Task:
        user_updated = await old_user.update(**new_user.__dict__).apply()
        return user_updated._instance

    async def delete_user(self, user_id: int) -> Task:
        return await Task.get(user_id).delete()

    async def get_user_byid(self, user_id: int) -> Task:
        return await Task.get(user_id)

    async def get_all_users(self) -> List[Task]:
        return await Task.query.gino.all()
