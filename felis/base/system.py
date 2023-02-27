import asyncio
from typing import Generic, Type, TypeVar
from .actor import Actor, ActorContext
from typing_extensions import Self

T = TypeVar("T")


class ActorSystem(Generic[T]):

    def __init__(
        self,
        root: Type[Actor[T]],
        name: str,
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        self.event_loop = loop
        self.root_context = ActorContext.of(self, event_loop=loop)
        self.root = root.of(name, self.root_context)

    @classmethod
    def of(
        cls,
        root: Type[Actor[T]],
        name: str,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> Self:
        return cls(root, name, loop or asyncio.get_event_loop())

    def start(self):
        self.event_loop.run_until_complete(self.root.stop())
