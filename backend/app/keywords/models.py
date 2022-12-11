from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class TimestampMixin:
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    modified_at = fields.DatetimeField(null=True, auto_now=True)


class Task(models.Model):
    id = fields.IntField(pk=True)
    keywords = fields.data.JSONField(default={})
    created_date = fields.DatetimeField(auto_now_add=True)

    # resources = relationship('Resource', back_populates='task')
    class Meta:
        table = "tasks"


class Resource(TimestampMixin, models.Model):
    id = fields.IntField(pk=True)
    domain = fields.CharField(max_length=255)
    task = fields.relational.ForeignKeyField("keywords.Task")
    done = fields.data.BooleanField(default=False)
    done_http = fields.data.BooleanField(default=False)
    done_https = fields.data.BooleanField(default=False)
    error_http = fields.data.TextField(null=True, default=None)
    error_https = fields.data.TextField(null=True, default=None)
    order = fields.BigIntField(null=True)

    def get_current_url(self):
        scheme = "http" if self.done_https else "https"
        resource_url = f"{scheme}://{self.domain}"
        return resource_url


class ResourceItem(TimestampMixin, models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255)
    resource = fields.relational.ForeignKeyField("keywords.Resource")
    done = fields.data.BooleanField(default=False)
    error = fields.data.TextField(null=True, default=None)
    keywords_found = fields.data.JSONField(default=[])


# Tortoise.init_models(["app.keywords.models"], "keywords")

Task_Pydantic = pydantic_model_creator(
    Task, name="Task", include=("id", "keywords", "created_date")
)
TaskIn_Pydantic = pydantic_model_creator(Task, name="TaskIn", exclude_readonly=True)

Resource_Pydantic = pydantic_model_creator(Resource, name="Resource")
ResourceIn_Pydantic = pydantic_model_creator(
    Resource, name="ResourceIn", exclude_readonly=True
)

ResourceItem_Pydantic = pydantic_model_creator(ResourceItem, name="ResourceItem")
ResourceItemIn_Pydantic = pydantic_model_creator(
    ResourceItem, name="ResourceItemIn", exclude_readonly=True
)
