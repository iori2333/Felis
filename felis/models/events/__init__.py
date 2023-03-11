from typing import Type

from .base import *
from .message import *
from .notice import *
from .meta import *

event_map: dict[str, Type[BaseEvent]] = {
    "connect": ConnectEvent,
    "heartbeat": HeartbeatEvent,
    "status_update": StatusUpdateEvent,
    "private": PrivateMessageEvent,
    "friend_increase": FriendIncreaseEvent,
    "friend_decrease": FriendDecreaseEvent,
    "private_message_delete": PrivateMessageDeleteEvent,
    "group": GroupMessageEvent,
    "group_member_increase": GroupMemberIncreaseEvent,
    "group_member_decrease": GroupMemberDecreaseEvent,
    "group_message_delete": GroupMessageDeleteEvent,
}
