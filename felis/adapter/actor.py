from typing import Type
from typing_extensions import Self
from pydantic import BaseModel

from .adapter import Adapters
from ..actor import ActorContext, Behavior, Behaviors, Future, ServiceKey, Routers
from ..messages.adapter import (
    AdapterMessage,
    AdapterTerminated,
    ClientAction,
    ServerData,
)
from ..messages.client import ClientMessage
from ..messages.driver import DriverMessage
from ..models.action import ActionResponse
from ..utils import LoggerLevel

EVENT_KEY = ServiceKey[ClientMessage]()
ACTION_KEY = ServiceKey[DriverMessage]()


class AdapterConfig(BaseModel):
    adapter_type: str = "onebot"
    connection_type: str = "websocket"


class AdapterActor:
    """
    AdapterActor: A bridge between Driver and Client. It processes raw data from the server and
    sends them back to the client.
    It also receives action requests from the client and sends them to the server.
    For extension, the events can be spread to other actors via event_router.

    +----------------+             +----------- -----+             +----------------+
    |                | Data -----> |                 | <-- Request |                |
    |     Driver     | ----------- |     Adapter     | Response -> |     Client     |
    |                | <-- Request |                 | Events ---> |                |
    +----------------+             +------------- ---+             +----------------+

    """

    def __init__(self, config: AdapterConfig) -> None:
        self.req_seq = 0
        self.future_store = dict[str, tuple[Future[ActionResponse], Type[BaseModel]]]()
        self.config = config
        AdapterType = Adapters.get(config.adapter_type)
        if AdapterType is None:
            raise ValueError(f"Unknown adapter type: {config.adapter_type}")
        self.adapter = AdapterType()

    @classmethod
    def of(cls, config: AdapterConfig | None = None) -> Self:
        return cls(config or AdapterConfig())

    def next_seq(self) -> str:
        self.req_seq += 1
        return str(self.req_seq)

    def apply(self) -> Behavior[AdapterMessage]:
        return Behaviors.setup(self.setup)

    def setup(self, context: ActorContext[AdapterMessage]) -> Behavior[AdapterMessage]:
        event_router = context.spawn(Routers.group(EVENT_KEY).apply(), "event_router")
        action_router = context.spawn(
            Routers.group(ACTION_KEY).apply(), "action_router"
        )

        def _apply(
            context: ActorContext[AdapterMessage], message: AdapterMessage
        ) -> Behavior[AdapterMessage]:
            match message:
                case ClientAction(action, future):
                    context.log(f"Sending action: {action}")
                    if future is not None:
                        seq, future = self.next_seq(), future
                        self.future_store[seq] = future, type(action)
                        action.echo = seq
                    action_router.tell(DriverMessage.of_action(action.dict()))
                case ServerData(data):
                    if self.adapter.is_response(data):
                        seq = data["echo"]
                        if seq not in self.future_store:
                            context.log(
                                f"Received data with seq={seq}, which is not found in future store.",
                                LoggerLevel.WARNING,
                            )
                            return Behavior[AdapterMessage].same
                        future, action_type = self.future_store.pop(seq)
                        future.set_result(
                            self.adapter.create_action_response(data, action_type)
                        )
                    else:
                        # send event to actors that subscribes EVENT_KEY
                        event = self.adapter.create_event(data)
                        context.log(f"Received event: {event}")
                        event_router.tell(ClientMessage.of_event(event))
                case AdapterTerminated():
                    return Behavior[AdapterMessage].stop
            return Behavior[AdapterMessage].same

        behavior = Behaviors.receive_message(_apply)
        return Behaviors.supervise(
            behavior, lambda _, __: Behavior[AdapterMessage].same
        )
