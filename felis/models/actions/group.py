from collections import UserList
from pydantic import BaseModel

from .base import BaseAction


class GroupInfoRequest(BaseAction):
    group_id: str


class GroupInfoResponse(BaseModel):
    group_id: str
    group_name: str


class GroupListRequest(BaseAction):
    pass


class GroupListResponse(UserList[GroupInfoResponse]):
    pass


class GroupMemberInfoRequest(BaseAction):
    group_id: str
    user_id: str


class GroupMemberInfoResponse(BaseModel):
    user_id: str
    user_name: str
    user_displayname: str


class GroupMemberListRequest(BaseAction):
    group_id: str


class GroupMemberListResponse(UserList[GroupMemberInfoResponse]):
    pass


class SetGroupNameRequest(BaseAction):
    group_id: str
    group_name: str


class LeaveGroupRequest(BaseAction):
    group_id: str
