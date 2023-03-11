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


class Register(Generic[T], ReceptionistRequest):
    def __init__(self, key: ServiceKey[T], actor: ActorRef[T]) -> None:
        self.key = key
        self.actor = actor


class Deregister(Generic[T], ReceptionistRequest):
    def __init__(self, key: ServiceKey[T], actor: ActorRef[T]) -> None:
        self.key = key
        self.actor = actor


class Find(Generic[T, U], ReceptionistRequest):
    def __init__(
        self,
        key: ServiceKey[T],
        adapter: Callable[[ListingResponse[T]], U],
        reply_to: ActorRef[U],
    ) -> None:
        self.key = key
        self.adapter = adapter
        self.reply_to = reply_to


class Subscribe(Generic[T], ReceptionistRequest):
    def __init__(self, key: ServiceKey[T], actor: ActorRef[ListingResponse[T]]) -> None:
        self.key = key
        self.actor = actor


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
        if isinstance(message, Register):
            key = message.key
            actor = message.actor
            if key not in cls.actor_map:
                cls.actor_map[key] = []
            cls.actor_map[key].append(actor)
            context.log(f"Registered actor {actor.path} with {key}.")
            for subscription in cls.subscription_map.get(key, []):
                subscription.tell(ListingResponse(*cls.actor_map[key]))
        elif isinstance(message, Deregister):
            key = message.key
            actor = message.actor
            if key in cls.actor_map:
                cls.actor_map[key].remove(actor)
            context.log(f"Deregistered actor {actor.path} with {key}.")
            for subscription in cls.subscription_map.get(key, []):
                subscription.tell(ListingResponse(*cls.actor_map[key]))
        elif isinstance(message, Find):
            key = message.key
            adapter = message.adapter
            reply_to = message.reply_to
            if key not in cls.actor_map:
                response = ListingResponse()
            else:
                response = ListingResponse(*cls.actor_map[key])
            context.log(f"Found {len(response)} with {key}, sending to {reply_to}.")
            reply_to.tell(adapter(response))
        elif isinstance(message, Subscribe):
            key = message.key
            actor = message.actor
            if key not in cls.subscription_map:
                cls.subscription_map[key] = []
            cls.subscription_map[key].append(actor)
            context.log(f"Added subscription for {actor.path} with topic {key}.")
        return Behavior[ReceptionistRequest].same
