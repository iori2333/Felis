from typing import Sequence
from typing_extensions import Self
from pydantic import BaseModel

from .command import Command
from .register import Commands
from ..actor import ActorRef
from ..utils import LoggerLevel
from ..adapter import EVENT_KEY, AdapterMessage
from ..actor import Behavior, Behaviors, ReceptionistRequest, ActorContext
from ..models.event import BaseEvent


class ClientConfig(BaseModel):
    commands: list[str] = ["echo"]


class ClientActor:
    def __init__(self, config: ClientConfig, adapter: ActorRef[AdapterMessage]) -> None:
        self._config = config
        self._adapter = adapter

    @classmethod
    def of(cls, config: ClientConfig, adapter: ActorRef[AdapterMessage]) -> Self:
        return cls(config, adapter)

    def apply(self) -> Behavior[BaseEvent]:
        return Behaviors.setup(self.setup)

    def setup(self, context: ActorContext[BaseEvent]) -> Behavior[BaseEvent]:
        commands = list[Command]()
        context.system.receptionist.tell(
            ReceptionistRequest.register(EVENT_KEY, context.self)
        )
        for name in self.commands:
            context.log(f"Registering command {name}")
            command = Commands.get(name)
            if command is None:
                context.log(f"Command {name} not found.", LoggerLevel.ERROR)
            else:
                commands.append(command(context, self._adapter))

        def on_message(
            context: ActorContext[BaseEvent], message: BaseEvent
        ) -> Behavior[BaseEvent]:
            for command in commands:
                if command.accepts(message):
                    context.log(f"running command {command.name}")
                    context.loop.create_task(command.execute(message))
            return Behavior[BaseEvent].same

        return Behaviors.receive_message(on_message)

    @property
    def commands(self) -> Sequence[str]:
        return self._config.commands
