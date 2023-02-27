from pydantic import BaseModel
from .message import Message
from .self import Self


class Event(BaseModel):
    id: str
    self: Self
    time: float
    type: str
    detail_type: str
    sub_type: str
    message_id: str
    message: Message
    alt_message: str
    user_id: str
