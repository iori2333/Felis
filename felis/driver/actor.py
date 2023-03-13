from typing_extensions import Self
from pydantic import BaseModel

from .backend import Backends
from ..actor import Behavior, Behaviors, ActorContext, ActorRef, ReceptionistRequest
from ..adapter import ACTION_KEY
from ..messages.adapter import AdapterMessage
from ..messages.driver import (
    AdapterAction,
    BackendClosed,
    DriverMessage,
    BackendData,
    BackendError,
)
from ..utils import LoggerLevel


class DriverConfig(BaseModel):
    backend_type: str = "websocket_reverse"
    connect_url: str
    access_token: str | None = None
    retry_interval: float = 5.0


class DriverActor:
    def __init__(self, config: DriverConfig, adapter: ActorRef[AdapterMessage]) -> None:
        self._config = config
        self._adapter = adapter
        BackendType = Backends.get(self._config.backend_type)
        if BackendType is None:
            raise ValueError(f"Unknown backend type: {self._config.backend_type}")
        self._backend_type = BackendType

    @classmethod
    def of(cls, config: DriverConfig, adapter: ActorRef[AdapterMessage]) -> Self:
        return cls(config, adapter)

    def apply(self) -> Behavior[DriverMessage]:
        return Behaviors.setup(self.setup)

    def setup(self, context: ActorContext[DriverMessage]) -> Behavior[DriverMessage]:
        backend = self._backend_type.of(context.self, self._config.connect_url)
        backend_task = lambda: context.loop.create_task(backend.start())
        backend_task()
        context.system.receptionist.tell(
            ReceptionistRequest.register(ACTION_KEY, context.self)
        )

        def on_message(
            context: ActorContext[DriverMessage], message: DriverMessage
        ) -> Behavior[DriverMessage]:
            match message:
                case BackendData(data):
                    context.log(f"Received data: {data}")
                    self._adapter.tell(AdapterMessage.of_response(data))
                case BackendError(error):
                    context.log(f"Received error: {error}", LoggerLevel.ERROR)
                case BackendClosed():
                    context.log(
                        f"Backend closed, retrying in {self._config.retry_interval} seconds...",
                        LoggerLevel.ERROR,
                    )
                    context.loop.call_later(self._config.retry_interval, backend_task)
                case AdapterAction(action):
                    context.log(f"Sending action: {action}")
                    backend.send(action)
            return Behavior[DriverMessage].same

        return Behaviors.receive_message(on_message)
