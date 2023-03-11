from .base import BaseEvent
from ..actions.meta import StatusResponse, VersionResponse


class MetaEvent(BaseEvent):
    pass


class ConnectEvent(MetaEvent):
    version: VersionResponse


class HeartbeatEvent(MetaEvent):
    interval: int


class StatusUpdateEvent(MetaEvent):
    status: StatusResponse
