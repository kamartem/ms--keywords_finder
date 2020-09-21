from sqlalchemy import ARRAY, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Resource(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    done = Column(Boolean, default=False)
    keywords_found = Column(ARRAY(String))

    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship('Task', back_populates='resources')

    resource_items = relationship('ResourceItem', back_populates='resource')
