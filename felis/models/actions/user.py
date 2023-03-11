from collections import UserList
from pydantic import BaseModel


class SelfInfoRequest(BaseModel):
    pass


class SelfInfoResponse(BaseModel):
    user_id: str
    user_name: str
    user_displayname: str


class UserInfoRequest(BaseModel):
    user_id: str


class UserInfoResponse(BaseModel):
    user_id: str
    user_name: str
    user_displayname: str
    user_remark: str


class FriendListRequest(BaseModel):
    pass


class FriendListResponse(UserList[UserInfoResponse]):
    pass
