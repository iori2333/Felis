from pydantic import BaseModel


class NotifyEvent(BaseModel):
    detail_type: str
    user_id: str


class GroupNotifyEvent(NotifyEvent):
    group_id: str


class FriendIncreaseEvent(NotifyEvent):
    pass


class FriendDecreaseEvent(NotifyEvent):
    pass


class PrivateMessageDeleteEvent(NotifyEvent):
    message_id: str


class GroupMemberIncreaseEvent(GroupNotifyEvent):
    sub_type: str
    operator_id: str


class GroupMemberDecreaseEvent(GroupNotifyEvent):
    sub_type: str
    operator_id: str


class GroupMessageDeleteEvent(GroupNotifyEvent):
    sub_type: str
    message_id: str
    operator_id: str
