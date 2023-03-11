from pydantic import BaseModel


class GroupInfoRequest(BaseModel):
    group_id: str


class GroupInfoResponse(BaseModel):
    group_id: str
    group_name: str


class GroupListRequest(BaseModel):
    pass


GroupListResponse = list[GroupInfoResponse]


class GroupMemberInfoRequest(BaseModel):
    group_id: str
    user_id: str


class GroupMemberInfoResponse(BaseModel):
    user_id: str
    user_name: str
    user_displayname: str


class GroupMemberListRequest(BaseModel):
    group_id: str


GroupMemberListResponse = list[GroupMemberInfoResponse]


class SetGroupNameRequest(BaseModel):
    group_id: str
    group_name: str


class LeaveGroupRequest(BaseModel):
    group_id: str
