from pydantic import BaseModel
from ..message import Message


class MessageEvent(BaseModel):
    detail_type: str
    message_id: str
    message: Message
    alt_message: str
    user_id: str


class PrivateMessageEvent(MessageEvent):
    pass


class GroupMessageEvent(MessageEvent):
    group_id: str
