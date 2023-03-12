from typing import Generic, Type, TypeVar

from ...actor import ActorRef, ActorContext, Behavior, Behaviors, Signal
from .receptionist import ServiceKey, ListingResponse, ReceptionistRequest

T = TypeVar("T")


class GroupForwarder(Generic[T]):
    def __init__(self, key: ServiceKey[T]) -> None:
        self._key = key
        self._workers: list[ActorRef[T]] = []

    def apply(self) -> Behavior[T | ListingResponse[T]]:
        return Behaviors.setup(self.setup)

    def setup(
        self, context: ActorContext[T | ListingResponse[T]]
    ) -> Behavior[T | ListingResponse[T]]:
        context.system.receptionist.tell(
            ReceptionistRequest.subscribe(self._key, context.self)  # type: ignore
        )
        return Behaviors.receive(self.on_receive)

    def on_receive(
        self,
        context: ActorContext[T | ListingResponse[T]],
        message: T | ListingResponse[T] | Signal,
    ) -> Behavior[T | ListingResponse[T]]:
        if isinstance(message, ListingResponse):
            self._workers = list(message.actors)
            return Behavior[T | ListingResponse[T]].same

        if isinstance(message, Signal):
            for worker in self._workers:
                worker.receive_signal(message)
        else:
            for worker in self._workers:
                worker.tell(message)
        return Behavior[T | ListingResponse[T]].same


class Forwarders:
    @staticmethod
    def group(key: ServiceKey[T]) -> GroupForwarder[T]:
        return GroupForwarder(key)
