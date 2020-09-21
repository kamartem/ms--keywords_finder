import datetime

from sqlalchemy import ARRAY, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    keywords = Column(ARRAY(String))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    resources = relationship('Resource', back_populates='task')
