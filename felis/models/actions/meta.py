from pydantic import BaseModel

from ..self import BotStatus
from ..event import BaseEvent


class LatestEventsRequest(BaseModel):
    limit: int = 0
    offset: int = 0


LatestEventsResponse = list[BaseEvent]


class SupportedActionsRequest(BaseModel):
    pass


SupportedActionsResponse = list[str]


class StatusRequest(BaseModel):
    pass


class StatusResponse(BaseModel):
    good: bool
    bots: list[BotStatus]


class VersionRequest(BaseModel):
    pass


class VersionResponse(BaseModel):
    impl: str
    version: str
    onebot_version: str
