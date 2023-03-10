from dataclasses import dataclass
from typing import Callable, TypeVar, Generic

from ..context import ActorContext
from ..behavior import Behavior, Behaviors
from ..actor import ActorRef

T = TypeVar("T")
U = TypeVar("U")


class ServiceKey(Generic[T]):
    def __init__(self) -> None:
        self.key = object()

    def __repr__(self) -> str:
        return f"ServiceKey[{id(self.key)}]"


class ListingResponse(Generic[T]):
    def __init__(self, *actors: ActorRef[T]) -> None:
        self.actors = actors

    def __len__(self) -> int:
        return len(self.actors)


class ReceptionistRequest:
    @staticmethod
    def register(key: ServiceKey[T], actor: ActorRef[T]) -> "Register[T]":
        return Register(key, actor)

    @staticmethod
    def deregister(key: ServiceKey[T], actor: ActorRef[T]) -> "Deregister[T]":
        return Deregister(key, actor)

    @staticmethod
    def find(
        key: ServiceKey[T],
        adapter: Callable[[ListingResponse[T]], U],
        reply_to: ActorRef[U],
    ) -> "Find[T, U]":
        return Find(key, adapter, reply_to)

    @staticmethod
    def subscribe(
        key: ServiceKey[T], actor: ActorRef[ListingResponse[T]]
    ) -> "Subscribe[T]":
        return Subscribe(key, actor)


@dataclass
class Register(Generic[T], ReceptionistRequest):
    key: ServiceKey[T]
    actor: ActorRef[T]


@dataclass
class Deregister(Generic[T], ReceptionistRequest):
    key: ServiceKey[T]
    actor: ActorRef[T]


@dataclass
class Find(Generic[T, U], ReceptionistRequest):
    key: ServiceKey[T]
    adapter: Callable[[ListingResponse[T]], U]
    reply_to: ActorRef[U]


@dataclass
class Subscribe(Generic[T], ReceptionistRequest):
    key: ServiceKey[T]
    actor: ActorRef[ListingResponse[T]]


class Receptionist:
    # since type hints holds no runtime information, ServiceKey and ActorRef stored in
    # `actor_map` are not type checked.
    actor_map = dict[ServiceKey, list[ActorRef]]()
    subscription_map = dict[ServiceKey, list[ActorRef]]()

    @classmethod
    def apply(cls) -> Behavior[ReceptionistRequest]:
        return Behaviors.setup(cls._setup)

    @classmethod
    def _setup(
        cls, context: ActorContext[ReceptionistRequest]
    ) -> Behavior[ReceptionistRequest]:
        return Behaviors.receive_message(cls.on_message)

    @classmethod
    def on_message(
        cls, context: ActorContext[ReceptionistRequest], message: ReceptionistRequest
    ) -> Behavior[ReceptionistRequest]:
        match message:
            case Register(key, actor):
                if key not in cls.actor_map:
                    cls.actor_map[key] = []
                cls.actor_map[key].append(actor)
                context.log(f"Registered actor {actor.path} with {key}.")
                for subscription in cls.subscription_map.get(key, []):
                    subscription.tell(ListingResponse(*cls.actor_map[key]))
            case Deregister(key, actor):
                if key in cls.actor_map:
                    cls.actor_map[key].remove(actor)
                context.log(f"Deregistered actor {actor.path} with {key}.")
                for subscription in cls.subscription_map.get(key, []):
                    subscription.tell(ListingResponse(*cls.actor_map[key]))
            case Find(key, adapter, reply_to):
                response = ListingResponse(*cls.actor_map.get(key, []))
                context.log(f"Found {len(response)} with {key}, sending to {reply_to}.")
                reply_to.tell(adapter(response))
            case Subscribe(key, actor):
                if key not in cls.subscription_map:
                    cls.subscription_map[key] = []
                cls.subscription_map[key].append(actor)
                context.log(f"Added subscription for {actor.path} with topic {key}.")
                actor.tell(ListingResponse(*cls.actor_map.get(key, [])))
        return Behavior[ReceptionistRequest].same
