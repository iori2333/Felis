from .base import BaseEvent


class NotifyEvent(BaseEvent):
    user_id: str


class PrivateNotifyEvent(NotifyEvent):
    pass


class GroupNotifyEvent(NotifyEvent):
    group_id: str


class FriendIncreaseEvent(PrivateNotifyEvent):
    pass


class FriendDecreaseEvent(PrivateNotifyEvent):
    pass


class PrivateMessageDeleteEvent(PrivateNotifyEvent):
    message_id: str


class GroupMemberIncreaseEvent(GroupNotifyEvent):
    operator_id: str


class GroupMemberDecreaseEvent(GroupNotifyEvent):
    operator_id: str


class GroupMessageDeleteEvent(GroupNotifyEvent):
    message_id: str
    operator_id: str
