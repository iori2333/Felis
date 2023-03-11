from collections import UserList
from pydantic import BaseModel

from ..self import BotStatus
from ..events import BaseEvent

from .base import BaseAction


class LatestEventsRequest(BaseAction):
    limit: int = 0
    offset: int = 0


class LatestEventsResponse(UserList[BaseEvent]):
    pass


class SupportedActionsRequest(BaseAction):
    pass


class SupportedActionsResponse(UserList[str]):
    pass


class StatusRequest(BaseAction):
    pass


class StatusResponse(BaseModel):
    good: bool
    bots: list[BotStatus]


class VersionRequest(BaseAction):
    pass


class VersionResponse(BaseModel):
    impl: str
    version: str
    onebot_version: str
