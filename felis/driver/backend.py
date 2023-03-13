from abc import ABC, abstractmethod
from typing import Any, Mapping
from typing_extensions import Self

from ..actor.actor import ActorRef
from ..messages.driver import DriverMessage
from ..utils import Registry


class Backend(ABC):
    def __init__(
        self,
        driver_actor: "ActorRef[DriverMessage]",
        url: str,
        access_token: str | None,
    ) -> None:
        self.driver = driver_actor
        self.url = url
        self.access_token = access_token

    @classmethod
    def of(
        cls,
        driver_actor: "ActorRef[DriverMessage]",
        url: str,
        access_token: str | None = None,
    ) -> Self:
        return cls(driver_actor, url, access_token)

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    def send(self, data: Mapping[str, Any]) -> None:
        pass


class Backends(Registry[Backend]):
    pass
