from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Task(models.Model):
    id = fields.IntField(pk=True)
    keywords = fields.data.JSONField()
    created_date = fields.DatetimeField(auto_now_add=True)

    # resources = relationship('Resource', back_populates='task')
    class Meta:
        table = 'tasks'


Task_Pydantic = pydantic_model_creator(Task, name="Task")
TaskIn_Pydantic = pydantic_model_creator(Task, name="TaskIn", exclude_readonly=True)
