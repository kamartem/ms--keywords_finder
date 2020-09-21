from pydantic import BaseModel


class TextArea(BaseModel):
    urls: str
    keywords: str
