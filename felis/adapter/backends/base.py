from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, AsyncGenerator, Type

from ..models.action import ActionResponse
from ..models.event import BaseEvent
from ..models.actions import BaseAction

if TYPE_CHECKING:
    from felis.adapter import Adapter


class ResponseConverter(ABC):

    @abstractmethod
    @classmethod
    def json_to_response(cls, data: Any) -> ActionResponse:
        raise NotImplementedError()

    @abstractmethod
    @classmethod
    def json_to_event(cls, data: Any) -> BaseEvent:
        raise NotImplementedError()


class BaseBackend(ABC):

    EOF = object()

    def __init__(
        self,
        adapter: Adapter,
        converter: Type[ResponseConverter],
    ) -> None:
        self.adapter = adapter
        self.converter = converter

    @abstractmethod
    async def call_api(self, action: BaseAction) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def events(self) -> AsyncGenerator[Any, None]:
        raise NotImplementedError()

    async def call_action(self, action: BaseAction) -> ActionResponse:
        data = await self.call_api(action)
        data = self.converter.json_to_response(data)
        return data

    async def run(self):
        async for event in self.events():
            if event is self.EOF:
                await self.adapter.terminate()
                return
            event = self.converter.json_to_event(event)
            await self.adapter.push_event(event)
