from typing import Generic, TypeVar

from .actor import ActorRef
from .context import ActorContext
from .behavior import Behavior
from .internal.receptionist import Receptionist, ReceptionistRequest
from ..utils import logger

T = TypeVar("T")


class ActorSystem(Generic[T]):
    def __init__(self, behavior: Behavior[T], name: str) -> None:
        context = ActorContext.of(name, behavior, self)
        self._context = context
        self._root = context.self
        self._receptionist = context.spawn(Receptionist.apply(), f"{name}_receptionist")
        logger.info(
            f"Started actor system {self._root.path} with receptionist {self._receptionist.path}."
        )

    async def wait(self) -> None:
        await self._context.wait()

    @property
    def root(self) -> ActorRef[T]:
        return self._root

    @property
    def receptionist(self) -> ActorRef[ReceptionistRequest]:
        return self._receptionist
