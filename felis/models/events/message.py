from ..event import BaseEvent
from ..message import Message, MessageSegment


class MessageEvent(BaseEvent):
    message_id: str
    message: Message
    alt_message: str
    user_id: str

    def __init__(_self, **kwargs) -> None:
        super(BaseEvent, _self).__init__(**kwargs)
        segments = map(lambda data: MessageSegment(**data), kwargs.get("message", []))
        _self.message = Message.of(*segments)


class PrivateMessageEvent(MessageEvent):
    pass


class GroupMessageEvent(MessageEvent):
    group_id: str
