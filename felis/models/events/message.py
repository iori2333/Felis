from .base import BaseEvent
from ..message import Message


class MessageEvent(BaseEvent):
    message_id: str
    message: Message
    alt_message: str
    user_id: str


class PrivateMessageEvent(MessageEvent):
    pass


class GroupMessageEvent(MessageEvent):
    group_id: str
