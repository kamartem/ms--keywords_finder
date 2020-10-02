from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class ResourceItem(models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255)
    done = fields.data.BooleanField(default=False)
    keywords_found = fields.data.JSONField()
    resource = fields.relational.ForeignKeyField('keywords.Resource')


ResourceItem_Pydantic = pydantic_model_creator(ResourceItem, name="ResourceItem")
ResourceItemIn_Pydantic = pydantic_model_creator(ResourceItem, name="ResourceItemIn", exclude_readonly=True)
