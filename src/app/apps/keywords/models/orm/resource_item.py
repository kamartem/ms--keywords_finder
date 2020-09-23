from sqlalchemy.orm import relationship

from app.apps.keywords.models.orm.base import Base
from app.core.db import db


class ResourceItem(Base):
    __tablename__ = 'resource_items'

    id = db.Column(db.Integer, primary_key=True, index=True)
    url = db.Column(db.String)
    done = db.Column(db.Boolean, default=False)
    keywords_found = db.Column(db.ARRAY(db.String))

    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
    resource = relationship('Resource', back_populates='resource_items')
