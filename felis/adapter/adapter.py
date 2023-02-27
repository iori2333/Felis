from asyncio import Future
from typing_extensions import override
from .backends.base import AdapterBackend
from felis.base import Actor, Behavior, Message, cast


class AdapterMessage:
    pass


class ServerEvent(AdapterMessage):
    """event received from server"""
    pass


class ClientAction(AdapterMessage):
    """action sent to server"""
    pass


class AdapterTerminated(AdapterMessage):
    """stop running the adapter"""
    pass


class Adapter(Actor[AdapterMessage]):

    async def client(self, request: ClientAction, future: Future):
        pass

    async def adapter(self, request: ServerEvent):
        pass

    async def on_error(self, error: Exception) -> Behavior[AdapterMessage]:
        return Behavior[AdapterMessage].SAME

    @override
    async def apply(self) -> Behavior[AdapterMessage]:

        self.backend = AdapterBackend.of("default", self)

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
