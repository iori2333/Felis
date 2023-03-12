from typing_extensions import Self
from pydantic import BaseModel

from .mongo import MongoDatabase
from ..actor import ActorContext, Behavior, Behaviors, ReceptionistRequest
from ..adapter import EVENT_KEY
from ..messages.client import AdapterEvent, ClientMessage
from ..models.events.message import GroupMessageEvent, PrivateMessageEvent


class DatabaseConfig(BaseModel):
    name: str = "felis"
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    user: str | None
    password: str | None


class DatabaseActor:
    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config

    @classmethod
    def of(cls, config: DatabaseConfig) -> Self:
        return cls(config)

    def apply(self) -> Behavior[ClientMessage]:
        return Behaviors.setup(self.setup)

    def setup(self, context: ActorContext[ClientMessage]) -> Behavior[ClientMessage]:
        context.system.receptionist.tell(
            ReceptionistRequest.register(EVENT_KEY, context.self)
        )
        database = MongoDatabase(self._config)
        group_msg = database.get_collection("group_msg", GroupMessageEvent)
        private_msg = database.get_collection("private_msg", PrivateMessageEvent)

        def on_message(
            context: ActorContext[ClientMessage], message: ClientMessage
        ) -> Behavior[ClientMessage]:
            match message:
                case AdapterEvent(event):
                    if isinstance(event, GroupMessageEvent):
                        context.log(f"Saving group message: {event.message.as_text()}")
                        group_msg.save(event)
                    elif isinstance(event, PrivateMessageEvent):
                        context.log(
                            f"Saving private message: {event.message.as_text()}"
                        )
                        private_msg.save(event)
            return Behavior[ClientMessage].same

        return Behaviors.receive_message(on_message)
