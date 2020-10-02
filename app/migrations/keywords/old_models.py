from app.keywords.models.resource import *
from app.keywords.models.resource_item import *
from app.keywords.models.task import *

from tortoise import Model, fields

MAX_VERSION_LENGTH = 255


class Aerich(Model):
    version = fields.CharField(max_length=MAX_VERSION_LENGTH)
    app = fields.CharField(max_length=20)

    class Meta:
        ordering = ["-id"]

