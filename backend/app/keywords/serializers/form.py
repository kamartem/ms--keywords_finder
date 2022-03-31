from pydantic import BaseModel


class TextAreaTask(BaseModel):
    urls: str
    keywords: str
