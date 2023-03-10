from typing import Generic, TypeVar

from .context import ActorContext
from .behavior import Behavior

T = TypeVar("T")


class ActorSystem(Generic[T]):
    def __init__(self, behavior: Behavior[T], name: str) -> None:
        context = ActorContext.of(name, behavior, self)
        self._context = context
        self._root = context.self

    async def wait(self) -> None:
        await self._context.wait()
