from pydantic import BaseModel, validator

from ..message import Message
from .base import BaseAction


class SendMessageRequest(BaseAction):
    detail_type: str
    user_id: str | None
    group_id: str | None
    guild_id: str | None
    channel_id: str | None
    message: Message

    @validator("user_id")
    def expect_private(cls, v, values):
        if values["detail_type"] == "private":
            assert v is not None
        return v

    @validator("group_id")
    def expect_group(cls, v, values):
        if values["detail_type"] == "group":
            assert v is not None
        return v

    @validator("guild_id", "channel_id")
    def expect_guild(cls, v, values):
        if values["detail_type"] == "channel":
            assert v is not None
        return v


class SendMessageResponse(BaseModel):
    message_id: str
    time: float


class DeleteMessageRequest(BaseAction):
    message_id: str
