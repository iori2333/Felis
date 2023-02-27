from collections import UserList
from pydantic import BaseModel

from .base import BaseAction


class SelfInfoRequest(BaseAction):
    pass


class SelfInfoResponse(BaseModel):
    user_id: str
    user_name: str
    user_displayname: str


class UserInfoRequest(BaseAction):
    user_id: str


class UserInfoResponse(BaseModel):
    user_id: str
    user_name: str
    user_displayname: str
    user_remark: str


class FriendListRequest(BaseAction):
    pass


class FriendListResponse(UserList[UserInfoResponse]):
    pass
