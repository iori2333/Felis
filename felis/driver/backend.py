from abc import ABC, abstractmethod
from typing import Any, Mapping
from typing_extensions import Self

from ..actor.actor import ActorRef
from ..messages.driver import DriverMessage
from ..utils import Registry


class Backend(ABC):
    def __init__(self, driver_actor: "ActorRef[DriverMessage]", url: str) -> None:
        self.driver = driver_actor
        self.url = url

    @classmethod
    def of(cls, driver_actor: "ActorRef[DriverMessage]", url: str) -> Self:
        return cls(driver_actor, url)

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    def send(self, data: Mapping[str, Any]) -> None:
        pass


class Backends(Registry[Backend]):
    pass
