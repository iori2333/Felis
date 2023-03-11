import asyncio
import os
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .behavior import Behavior, Behaviors
from ..utils import LoggerLevel

if TYPE_CHECKING:
    from .context import ActorContext
from .signals import Signal

T = TypeVar("T")


class ActorRef(Generic[T]):
    def __init__(self, actor: "Actor[T]", parent: "ActorContext[Any] | None") -> None:
        self._actor = actor
        if parent is None:
            self._base_url = "/"
        else:
            self._base_url = parent.self.path

    @property
    def path(self) -> str:
        return os.path.join(self._base_url, self._actor._name)

    @property
    def name(self) -> str:
        return self._actor._name

    @classmethod
    def of(
        cls, actor: "Actor[T]", parent: "ActorContext[Any] | None" = None
    ) -> "ActorRef[T]":
        return cls(actor, parent)

    @property
    def ref(self) -> "Actor[T]":
        return self._actor

    def tell(self, message: T) -> None:
        self._actor.tell(message)

    def receive_signal(self, signal: Signal) -> None:
        self._actor.tell(signal)

    def __repr__(self) -> str:
        return f"ActorRef[path={self.path}]"


class Actor(Generic[T]):
    def __init__(
        self, name: str, behavior: Behavior[T], context: "ActorContext[T]"
    ) -> None:
        self._name = name
        self._mailbox = asyncio.Queue[T | Signal]()
        self._behavior = behavior
        self._context = context
        self._stopped = False

    async def _start(self):
        try:
            current = self._behavior.apply(self._context)
            while current is not Behaviors.stop:
                msg = await self._mailbox.get()
                next = current.on_receive(self._context, msg)
                self._mailbox.task_done()
                if next is Behaviors.same:
                    continue
                current = next
        except asyncio.CancelledError:
            self._context.log(f"Actor {self._name} is cancelled.")
            self._stopped = True
        if not self._mailbox.empty():
            self._context.log(
                f"Actor {self._name} stopped, but there are still {self._mailbox.qsize()} messages in the mailbox.",
                LoggerLevel.WARNING,
            )

    @property
    def is_alive(self) -> bool:
        return not self._stopped

    def tell(self, message: T | Signal):
        if not self.is_alive:
            raise RuntimeError("Actor is already stopped")
        self._mailbox.put_nowait(message)
