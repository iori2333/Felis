from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from .resource import ResourceManager

from ..actor import ActorRef, ActorContext
from ..messages.adapter import AdapterMessage
from ..messages.client import ClientMessage
from ..models.action import Action
from ..models.actions import SendMessageRequest
from ..models.event import BaseEvent
from ..models.events import MessageEvent
from ..models.message import Message


T = TypeVar("T", bound=BaseEvent)


class Command(ABC, Generic[T]):
    name: str
    prefix: str | None
    aliases: list[str]
    description: str

    def __init__(
        self,
        context: ActorContext[ClientMessage],
        adapter: ActorRef[AdapterMessage],
        resources: ResourceManager,
    ) -> None:
        self.context = context
        self.adapter = adapter
        self.resources = resources

    @abstractmethod
    async def execute(self, event: T) -> None:
        raise NotImplementedError()

    def accepts(self, event: BaseEvent) -> bool:
        accepted_type = self.execute.__annotations__.get("event", None)
        if accepted_type is None:
            return True
        return isinstance(event, accepted_type)

    def send_back(self, event: T, message: Message) -> None:
        if type(event).__name__.startswith("Group"):
            self.send_group_message(event.group_id, message)  # type: ignore
        elif type(event).__name__.startswith("Private"):
            self.send_private_message(event.user_id, message)  # type: ignore
        else:
            return

    def send_group_message(self, group_id: str, message: Message) -> None:
        self.adapter.tell(
            AdapterMessage.of_action(
                Action.of(SendMessageRequest.group(group_id, message))
            )
        )

    def send_private_message(self, user_id: str, message: Message) -> None:
        self.adapter.tell(
            AdapterMessage.of_action(
                Action.of(SendMessageRequest.private(user_id, message))
            )
        )

    async def call_action(
        self,
        action: Action,
        timeout: float = 5.0,
    ) -> Any:
        future = self.context.ask(
            self.adapter,
            lambda f: AdapterMessage.of_action(action, f),
            timeout=timeout,
        )
        return await future


class MessageCommand(Command[MessageEvent]):
    async def execute(self, event: MessageEvent) -> None:
        command, message = event.message.split_first()
        if self.prefix is not None and not command.startswith(self.prefix):
            return

        if self.prefix is not None:
            command = command.removeprefix(self.prefix)

        if command == self.name or command in self.aliases:
            await self.handle_message(event, message)

    @abstractmethod
    async def handle_message(self, event: MessageEvent, message: Message) -> None:
        raise NotImplementedError()
