from tortoise import Tortoise, fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Resource(models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255)
    done = fields.data.BooleanField(default=False)
    keywords_found = fields.data.JSONField(default=[])
    task = fields.relational.ForeignKeyField('keywords.Task')
    had_error = fields.data.BooleanField(default=False)

    # resource_items = relationship('ResourceItem', back_populates='resource')


Tortoise.init_models(["app.keywords.models.task", "app.keywords.models.resource"], "keywords")
Resource_Pydantic = pydantic_model_creator(Resource, name="Resource")
ResourceIn_Pydantic = pydantic_model_creator(Resource, name="ResourceIn", exclude_readonly=True)
