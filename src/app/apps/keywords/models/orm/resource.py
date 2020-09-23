from sqlalchemy.orm import relationship

from app.apps.keywords.models.orm.base import Base
from app.core.db import db


class Resource(Base):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True, index=True)
    url = db.Column(db.String)
    done = db.Column(db.Boolean, default=False)
    keywords_found = db.Column(db.ARRAY(db.String))

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    task = relationship('Task', back_populates='resources')

    resource_items = relationship('ResourceItem', back_populates='resource')
