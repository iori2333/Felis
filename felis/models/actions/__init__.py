from typing import Any, Type
from .group import *
from .message import *
from .user import *
from .file import *
from .meta import *

action_map: dict[Type[BaseModel], str] = {
    SendMessageRequest: "send_message",
    DeleteMessageRequest: "delete_message",
    SelfInfoRequest: "get_self_info",
    UserInfoRequest: "get_user_info",
    FriendListRequest: "get_friend_list",
    GroupListRequest: "get_group_list",
    GroupInfoRequest: "get_group_info",
    GroupMemberListRequest: "get_group_member_list",
    GroupMemberInfoRequest: "get_group_member_info",
    SetGroupNameRequest: "set_group_name",
    LeaveGroupRequest: "leave_group",
    UploadFileRequest: "upload_file",
    UploadFileFragmentedRequest.Prepare: "upload_file_fragmented",
    UploadFileFragmentedRequest.Upload: "upload_file_fragmented",
    UploadFileFragmentedRequest.Complete: "upload_file_fragmented",
    FileRequest: "get_file",
    FileFragmentedRequest.Prepare: "get_file_fragmented",
    FileFragmentedRequest.Download: "get_file_fragmented",
    # LatestEventsRequest: "get_latest_events",
    SupportedActionsRequest: "get_supported_actions",
    StatusRequest: "get_status",
    VersionRequest: "get_version",
}

response_map: dict[Type[BaseModel], Type[Any] | tuple[Type[Any], ...]] = {
    SendMessageRequest: SendMessageResponse,
    # DeleteMessageRequest: DeleteMessageResponse,
    SelfInfoRequest: SelfInfoResponse,
    UserInfoRequest: UserInfoResponse,
    FriendListRequest: (FriendListResponse, UserInfoResponse),
    GroupListRequest: (GroupListResponse, GroupInfoResponse),
    GroupInfoRequest: GroupInfoResponse,
    GroupMemberListRequest: (GroupMemberListResponse, GroupMemberInfoResponse),
    GroupMemberInfoRequest: GroupMemberInfoResponse,
    # SetGroupNameRequest: SetGroupNameResponse,
    # LeaveGroupRequest: LeaveGroupResponse,
    UploadFileRequest: UploadFileResponse,
    UploadFileFragmentedRequest.Prepare: UploadFileFragmentedResponse.Prepare,
    # UploadFileFragmentedRequest.Upload: UploadFileFragmentedResponse.Complete,
    UploadFileFragmentedRequest.Complete: UploadFileFragmentedResponse.Complete,
    FileRequest: FileResponse,
    FileFragmentedRequest.Prepare: FileFragmentedResponse.Prepare,
    FileFragmentedRequest.Download: FileFragmentedResponse.Download,
    # LatestEventsRequest: LatestEventsResponse,
    SupportedActionsRequest: (SupportedActionsResponse, str),
    StatusRequest: StatusResponse,
    VersionRequest: VersionResponse,
}
