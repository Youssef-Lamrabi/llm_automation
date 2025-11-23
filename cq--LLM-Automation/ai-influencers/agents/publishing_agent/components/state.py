from pydantic import BaseModel
from typing import Optional, Dict

class PublishState(BaseModel):
    platform: str
    content: str
    title: Optional[str] = None
    tags: Optional[list] = None
    scheduled_time: Optional[str] = None
    status: str = "pending"
    response: Optional[Dict] = None
