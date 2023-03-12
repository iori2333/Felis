from ..models.event import BaseEvent


class ClientMessage:
    @staticmethod
    def of_event(event: BaseEvent) -> "AdapterEvent":
        return AdapterEvent(event)


class AdapterEvent(ClientMessage):
    def __init__(self, event: BaseEvent) -> None:
        self.event = event
