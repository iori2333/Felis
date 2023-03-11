from abc import abstractmethod
from typing import Generic, Sequence, Type, TypeVar
import random

from .receptionist import ListingResponse, ReceptionistRequest, ServiceKey
from ..signals import Signal, Terminated
from ..actor import ActorRef
from ..context import ActorContext
from ..behavior import Behavior, Behaviors

T = TypeVar("T")


class Executor(Generic[T]):
    """Executor selects a worker from a pool of workers."""

    @classmethod
    @abstractmethod
    def get_worker(
        cls, workers: Sequence[ActorRef[T]], context: ActorContext[T]
    ) -> ActorRef[T] | None:
        raise NotImplementedError()


class DefaultExecutor(Executor[T]):
    """Default executor for routers. It randomly selects a worker from the list."""

    @classmethod
    def get_worker(
        cls, workers: Sequence[ActorRef[T]], _: ActorContext[T]
    ) -> ActorRef[T] | None:
        if len(workers) == 0:
            return None
        choice = random.choice(workers)
        while not choice.ref.is_alive:
            choice = random.choice(workers)
        return choice


class PoolRouter(Generic[T]):
    def __init__(
        self,
        size: int,
        behavior: Behavior[T],
        executor: Type[Executor],
    ) -> None:
        self._behavior = behavior
        self._size = size
        self._executor = executor
        self._workers: list[ActorRef[T]] = []

    def apply(self) -> Behavior[T]:
        return Behaviors.setup(self.setup)

    def setup(self, context: ActorContext[T]) -> Behavior[T]:
        for i in range(self._size):
            ref = context.spawn(self._behavior, f"worker_{i}")
            context.watch(ref)
            self._workers.append(ref)
        return Behaviors.receive(self.on_receive)

    def on_receive(self, context: ActorContext[T], message: T | Signal) -> Behavior[T]:
        worker = self._executor.get_worker(self._workers, context)
        if worker is None:
            return Behavior[T].stop
        if isinstance(message, Terminated):
            if message.ref in self._workers:
                self._workers.remove(message.ref)
            if len(self._workers) == 0:
                return Behavior[T].stop
        elif isinstance(message, Signal):
            worker.receive_signal(message)
        else:
            worker.tell(message)
        return Behavior[T].same


class GroupRouter(Generic[T]):
    def __init__(self, key: ServiceKey[T], executor: Type[Executor]) -> None:
        self._key = key
        self._executor = executor
        self._stashed: list[T | Signal] = []
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
            self.handle_stashed(context)
            return Behavior[T | ListingResponse[T]].same

        worker = self._executor.get_worker(self._workers, context)
        if worker is None:
            self._stashed.append(message)
            return Behavior[T | ListingResponse[T]].same

        if isinstance(message, Signal):
            worker.receive_signal(message)
        else:
            worker.tell(message)
        return Behavior[T | ListingResponse[T]].same

    def handle_stashed(self, context: ActorContext[T | ListingResponse[T]]) -> None:
        for message in self._stashed:
            worker = self._executor.get_worker(self._workers, context)
            if worker is None:
                return
            if isinstance(message, Signal):
                worker.receive_signal(message)
            else:
                worker.tell(message)
        self._stashed = []


class Routers:
    @staticmethod
    def pool(
        size: int, behavior: Behavior[T], executor: Type[Executor] = DefaultExecutor
    ) -> PoolRouter[T]:
        return PoolRouter(size, behavior, executor)

    @staticmethod
    def group(
        key: ServiceKey[T], executor: Type[Executor] = DefaultExecutor
    ) -> GroupRouter[T]:
        return GroupRouter(key, executor)
