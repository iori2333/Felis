from typing import Mapping, Any
from pydantic import BaseModel

from ..actor import Future
from ..models.action import ActionResponse


class AdapterMessage:
    @staticmethod
    def of_response(data: Mapping[str, Any]) -> "AdapterMessage":
        return ServerData(data)

    @staticmethod
    def of_action(
        action: BaseModel, future: Future[ActionResponse] | None = None
    ) -> "AdapterMessage":
        return ClientAction(action, future)

    @staticmethod
    def of_terminated() -> "AdapterMessage":
        return AdapterTerminated()


class ServerData(AdapterMessage):
    """event received from server"""

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.data = data


class ClientAction(AdapterMessage):
    """action sent to server"""

    def __init__(self, action: BaseModel, future: Future | None) -> None:
        self.action = action
        self.future = future


class AdapterTerminated(AdapterMessage):
    """stop running the adapter"""

    pass
