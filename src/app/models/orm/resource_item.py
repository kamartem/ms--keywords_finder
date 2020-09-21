from sqlalchemy import ARRAY, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class ResourceItem(Base):
    __tablename__ = 'resource_items'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    done = Column(Boolean, default=False)
    keywords_found = Column(ARRAY(String))

    resource_id = Column(Integer, ForeignKey('resources.id'))
    resource = relationship('Resource', back_populates='resource_items')
