from typing import List

from pydantic import BaseModel


class ResourceBase(BaseModel):
    url: str


class ResourceCreate(ResourceBase):
    pass


class Resource(ResourceBase):
    id: int
    done: bool
    keywords_found: List[str] = []

    class Config:
        orm_mode = True
