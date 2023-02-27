from ..actions.meta import StatusResponse, VersionResponse
from ..event import BaseEvent


class MetaEvent(BaseEvent):
    pass


class ConnectEvent(MetaEvent):
    version: VersionResponse


class HeartbeatEvent(MetaEvent):
    interval: int


class StatusUpdateEvent(MetaEvent):
    status: StatusResponse
