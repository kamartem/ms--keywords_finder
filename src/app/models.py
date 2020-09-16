from sqlalchemy import ARRAY, Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    keywords = Column(ARRAY(String))

    resources = relationship('Resource', back_populates='task')


class Resource(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    done = Column(Boolean, default=False)
    keywords_found = Column(ARRAY(String))

    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship('Task', back_populates='resources')
