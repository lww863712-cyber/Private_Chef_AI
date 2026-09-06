from typing import Optional

from pydantic.v1 import BaseModel


class ChatRequest(BaseModel):
    message:str
    image_url : Optional[str] = None
    thread_id: str