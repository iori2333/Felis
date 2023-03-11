from pydantic import BaseModel, validator
from typing_extensions import Self
from ..message import Message


class SendMessageRequest(BaseModel):
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

    @classmethod
    def group(cls, group_id: str, message: Message) -> Self:
        return cls(
            detail_type="group",
            user_id=None,
            group_id=group_id,
            guild_id=None,
            channel_id=None,
            message=message,
        )

    @classmethod
    def private(cls, user_id: str, message: Message) -> Self:
        return cls(
            detail_type="private",
            user_id=user_id,
            group_id=None,
            guild_id=None,
            channel_id=None,
            message=message,
        )

    @classmethod
    def channel(cls, guild_id: str, channel_id: str, message: Message) -> Self:
        return cls(
            detail_type="channel",
            user_id=None,
            group_id=None,
            guild_id=guild_id,
            channel_id=channel_id,
            message=message,
        )


class SendMessageResponse(BaseModel):
    message_id: str
    time: float


class DeleteMessageRequest(BaseModel):
    message_id: str
