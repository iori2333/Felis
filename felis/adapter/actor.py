from typing import Any, Mapping, Type
from typing_extensions import Self
from pydantic import BaseModel

from .adapters import AdapterFactory
from ..actor import ActorContext, Behavior, Behaviors, Future, ServiceKey, Routers
from ..models.action import ActionResponse
from ..models.events import BaseEvent
from ..utils import LoggerLevel

EVENT_KEY = ServiceKey[BaseEvent]()


class AdapterConfig(BaseModel):
    adapter_type: str = "onebot"
    connection_type: str = "websocket"


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
        self.adapter = AdapterFactory.get(config.adapter_type)

    @classmethod
    def of(cls, config: AdapterConfig | None = None) -> Self:
        return cls(config or AdapterConfig())

    def next_seq(self) -> str:
        self.req_seq += 1
        return str(self.req_seq)

    def apply(self) -> Behavior[AdapterMessage]:
        return Behaviors.setup(self.setup)

    def setup(self, context: ActorContext[AdapterMessage]) -> Behavior[AdapterMessage]:
        router = Routers.group(EVENT_KEY)
        router = context.spawn(router.apply(), "event_router")

        def _apply(
            context: ActorContext[AdapterMessage], message: AdapterMessage
        ) -> Behavior[AdapterMessage]:
            loop = context.loop
            if isinstance(message, ClientAction):
                context.log(f"Sending action: {message.action}")
                if message.future is not None:
                    seq, future = self.next_seq(), message.future
                    self.future_store[seq] = future, type(message.action)
                # create task that handles the api call
            elif isinstance(message, ServerData):
                if self.adapter.is_response(message.data):
                    seq = message.data["echo"]
                    if seq not in self.future_store:
                        context.log(
                            f"Received data with seq={seq}, which is not found in future store.",
                            LoggerLevel.WARNING,
                        )
                        return Behavior[AdapterMessage].same
                    future, action_type = self.future_store.pop(seq)
                    future.set_result(
                        self.adapter.create_action_response(message.data, action_type)
                    )
                else:
                    # send event to actors that subscribes EVENT_KEY
                    event = self.adapter.create_event(message.data)
                    context.log(f"Received event: {event}")
                    router.tell(event)
            else:
                return Behavior[AdapterMessage].stop
            return Behavior[AdapterMessage].same

        behavior = Behaviors.receive_message(_apply)
        return Behaviors.supervise(
            behavior, lambda _, __: Behavior[AdapterMessage].same
        )
