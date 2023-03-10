from dataclasses import dataclass
from typing import Mapping, Any

from ..actor import Future
from ..models.action import Action, ActionResponse


class AdapterMessage:
    @staticmethod
    def of_response(data: Mapping[str, Any]) -> "AdapterMessage":
        return ServerData(data)

    @staticmethod
    def of_action(
        action: Action, future: Future[ActionResponse] | None = None
    ) -> "AdapterMessage":
        return ClientAction(action, future)

    @staticmethod
    def of_terminated() -> "AdapterMessage":
        return AdapterTerminated()


@dataclass
class ServerData(AdapterMessage):
    data: Mapping[str, Any]


@dataclass
class ClientAction(AdapterMessage):
    """action sent to server"""

    action: Action
    future: Future | None = None


@dataclass
class AdapterTerminated(AdapterMessage):
    """stop running the adapter"""

    pass
