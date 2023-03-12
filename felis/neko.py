import asyncio
from pathlib import Path
from pydantic import BaseModel
from typing_extensions import Self

from .adapter.actor import AdapterConfig
from .client.actor import ClientConfig, ClientActor
from .driver.actor import DriverConfig, DriverActor

from .actor import ActorContext, Behavior, Behaviors, ActorSystem
from .adapter import AdapterActor


class NekoMessage:
    pass


class Sleep(NekoMessage):
    pass


class NekoConfig(BaseModel):
    name: str = "felis"
    adapter: AdapterConfig = AdapterConfig()
    client: ClientConfig = ClientConfig()
    driver: DriverConfig


class Neko:
    def __init__(self, config: NekoConfig) -> None:
        self._name = config.name
        self._config = config

    @classmethod
    def from_config(cls, config: NekoConfig) -> Self:
        return cls(config)

    @classmethod
    def from_file(cls, path: str | Path) -> Self:
        return cls.from_config(NekoConfig.parse_file(path))

    def apply(self) -> Behavior[NekoMessage]:
        return Behaviors.setup(self.setup)

    def customized_setup(self, context: ActorContext[NekoMessage]) -> None:
        """An extension point to add additional services."""
        pass

    def setup(self, context: ActorContext[NekoMessage]) -> Behavior[NekoMessage]:
        self.adapter = context.spawn(
            AdapterActor.of(self.config.adapter).apply(), name="adapter"
        )
        self.client = context.spawn(
            ClientActor.of(self.config.client, self.adapter).apply(), name="client"
        )
        self.driver = context.spawn(
            DriverActor.of(self.config.driver, self.adapter).apply(), name="driver"
        )
        # context.spawn(DatabaseActor.apply(), name="database")
        self.customized_setup(context)
        return Behavior[NekoMessage].same

    def on_message(self, _, message: NekoMessage) -> Behavior[NekoMessage]:
        if isinstance(message, Sleep):
            return Behavior[NekoMessage].stop
        return Behavior[NekoMessage].same

    @property
    def config(self) -> NekoConfig:
        return self._config

    @property
    def name(self) -> str:
        return self._name

    async def start(self):
        system = ActorSystem(self.apply(), self.name)
        await system.wait()

    def run(self):
        asyncio.run(self.start())
