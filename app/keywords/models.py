from tortoise import Tortoise, fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Task(models.Model):
    id = fields.IntField(pk=True)
    keywords = fields.data.JSONField()
    created_date = fields.DatetimeField(auto_now_add=True)

    # resources = relationship('Resource', back_populates='task')
    class Meta:
        table = 'tasks'


class Resource(models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255)
    done = fields.data.BooleanField(default=False)
    keywords_found = fields.data.JSONField(default=[])
    task = fields.relational.ForeignKeyField('keywords.Task')
    had_error = fields.data.BooleanField(default=False)
    error_reason = fields.data.TextField(null=True)

    # resource_items = relationship('ResourceItem', back_populates='resource')


class ResourceItem(models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255)
    done = fields.data.BooleanField(default=False)
    keywords_found = fields.data.JSONField(default=[])
    resource = fields.relational.ForeignKeyField('keywords.Resource')
    had_error = fields.data.BooleanField(default=False)
    error_reason = fields.data.TextField(null=True)


Tortoise.init_models(["app.keywords.models"], "keywords")

Task_Pydantic = pydantic_model_creator(Task, name="Task")
TaskIn_Pydantic = pydantic_model_creator(Task, name="TaskIn", exclude_readonly=True)

Resource_Pydantic = pydantic_model_creator(Resource, name="Resource")
ResourceIn_Pydantic = pydantic_model_creator(Resource, name="ResourceIn", exclude_readonly=True)

ResourceItem_Pydantic = pydantic_model_creator(ResourceItem, name="ResourceItem")
ResourceItemIn_Pydantic = pydantic_model_creator(ResourceItem, name="ResourceItemIn", exclude_readonly=True)
