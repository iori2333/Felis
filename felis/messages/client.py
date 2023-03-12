from dataclasses import dataclass
from ..models.event import BaseEvent


class ClientMessage:
    @staticmethod
    def of_event(event: BaseEvent) -> "AdapterEvent":
        return AdapterEvent(event)


@dataclass
class AdapterEvent(ClientMessage):
    event: BaseEvent
