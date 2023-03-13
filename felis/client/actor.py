from typing import Sequence
from typing_extensions import Self
from pydantic import BaseModel

from .command import Command
from .register import Commands
from .internal import internal_commands
from ..actor import Behavior, Behaviors, ReceptionistRequest, ActorContext, ActorRef
from ..adapter import EVENT_KEY
from ..messages.adapter import AdapterMessage
from ..messages.client import AdapterEvent, ClientMessage
from ..utils import LoggerLevel


class ClientConfig(BaseModel):
    commands: list[str] = internal_commands


class ClientActor:
    def __init__(self, config: ClientConfig, adapter: ActorRef[AdapterMessage]) -> None:
        self._config = config
        self._adapter = adapter

    @classmethod
    def of(cls, config: ClientConfig, adapter: ActorRef[AdapterMessage]) -> Self:
        return cls(config, adapter)

    def apply(self) -> Behavior[ClientMessage]:
        return Behaviors.setup(self.setup)

    def setup(self, context: ActorContext[ClientMessage]) -> Behavior[ClientMessage]:
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
            context: ActorContext[ClientMessage], message: ClientMessage
        ) -> Behavior[ClientMessage]:
            match message:
                case AdapterEvent(event):
                    for command in commands:
                        if command.accepts(event):
                            context.log(f"running command {command.name}")
                            context.loop.create_task(command.execute(event))
            return Behavior[ClientMessage].same

        return Behaviors.receive_message(on_message)

    @property
    def commands(self) -> Sequence[str]:
        return self._config.commands
