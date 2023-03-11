from abc import ABC, abstractmethod
from typing import Any, Mapping, Type
from pydantic import BaseModel

from ..models.events import BaseEvent
from ..models.action import ActionResponse


class Adapter(ABC):
    @abstractmethod
    def is_response(self, data: Mapping[str, Any]) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def create_action_response(
        self, data: Mapping[str, Any], action_type: Type[BaseModel]
    ) -> ActionResponse:
        raise NotImplementedError()

    @abstractmethod
    def create_event(self, data: Mapping[str, Any]) -> BaseEvent:
        raise NotImplementedError()
