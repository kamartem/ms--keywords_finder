import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    keywords = Column(ARRAY(String))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    resources = relationship('Resource', back_populates='task')


class Resource(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    done = Column(Boolean, default=False)
    keywords_found = Column(ARRAY(String))

    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship('Task', back_populates='resources')

    resource_items = relationship('ResourceItem', back_populates='resource')


class ResourceItem(Base):
    __tablename__ = 'resource_items'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    done = Column(Boolean, default=False)
    keywords_found = Column(ARRAY(String))

    resource_id = Column(Integer, ForeignKey('resources.id'))
    resource = relationship('Resource', back_populates='resource_items')
