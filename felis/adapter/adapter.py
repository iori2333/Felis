from asyncio import Future
from typing_extensions import override
from .backends import BackendFactory

from felis.base import Actor, Behavior, Message, cast

from .models.action import ActionResponse
from .models.actions import BaseAction
from .models.event import BaseEvent


class AdapterMessage:

    @staticmethod
    def of_event(event: BaseEvent) -> "AdapterMessage":
        return ServerEvent(event)

    @staticmethod
    def of_action(action: BaseAction) -> "AdapterMessage":
        return ClientAction(action)

    @staticmethod
    def of_terminated() -> "AdapterMessage":
        return AdapterTerminated()


class ServerEvent(AdapterMessage):
    """event received from server"""

    def __init__(self, event: BaseEvent) -> None:
        self.event = event


class ClientAction(AdapterMessage):
    """action sent to server"""

    def __init__(self, action: BaseAction) -> None:
        self.action = action


class AdapterTerminated(AdapterMessage):
    """stop running the adapter"""
    pass


class Adapter(Actor[AdapterMessage]):

    async def client(
        self,
        request: ClientAction,
        future: Future[ActionResponse],
    ) -> None:
        data = await self.backend.call_action(request.action)
        if data.status != "ok":
            future.set_exception(ConnectionAbortedError(data.message))
        else:
            future.set_result(data.data)

    async def adapter(self, request: ServerEvent) -> None:
        pass

    async def on_error(self, error: Exception) -> Behavior[AdapterMessage]:
        return Behavior[AdapterMessage].SAME

    async def push_event(self, event: BaseEvent) -> None:
        msg = AdapterMessage.of_event(event)
        await self._put(Message.of(msg))

    async def push_action(
        self,
        action: BaseAction,
        future: Future[ActionResponse],
    ) -> None:
        msg = AdapterMessage.of_action(action)
        await self._put(Message.of(msg, future))

    async def terminate(self) -> None:
        msg = AdapterMessage.of_terminated()
        await self._put(Message.of(msg))

    @override
    async def apply(self) -> Behavior[AdapterMessage]:
        self.backend = BackendFactory.of("default", self)

        async def _apply(
                message: Message[AdapterMessage]) -> Behavior[AdapterMessage]:
            if isinstance(message.payload, ClientAction):
                await self.client(
                    message.payload,
                    cast[Future](message.future),
                )
            elif isinstance(message.payload, ServerEvent):
                await self.adapter(message.payload)
            else:
                return Behavior[AdapterMessage].STOP
            return Behavior[AdapterMessage].SAME

        return Behavior.supervise(_apply, self.on_error)
