from typing import TYPE_CHECKING, Any, Callable, Generic, Iterable, TypeVar
import asyncio

from .signals import Terminated
from .future import Future
from .actor import Actor, ActorRef
from ..utils import Logger, LoggerLevel

if TYPE_CHECKING:
    from .system import ActorSystem
    from .behavior import Behavior

T = TypeVar("T")
U = TypeVar("U")


class ActorContext(Generic[T]):
    def __init__(
        self,
        name: str,
        behavior: "Behavior[T]",
        system: "ActorSystem[Any]",
        parent: "ActorContext[Any] | None",
    ) -> None:
        actor = Actor(name, behavior, self)
        self._self = ActorRef(actor, parent)
        self._children = dict[str, ActorContext[Any]]()
        self._system = system
        self._task = asyncio.create_task(actor._start())
        self._loop = asyncio.get_event_loop()

    @classmethod
    def of(
        cls,
        name: str,
        behavior: "Behavior[T]",
        system: "ActorSystem[Any]",
        parent: "ActorContext[Any] | None" = None,
    ) -> "ActorContext[T]":
        return cls(name, behavior, system, parent)

    def spawn(self, behavior: "Behavior[U]", name: str) -> ActorRef[U]:
        if name in self._children:
            self.log(f"Actor {name} already exists, ignoring.", LoggerLevel.ERROR)
        context = ActorContext(name, behavior, self._system, self)
        actor_ref = context.self
        self._children[name] = context
        self.log(f"Spawned actor {name} at {actor_ref.path}.")
        return actor_ref

    def stop(self, actor: ActorRef[Any]) -> None:
        if self._children.get(actor.name) != actor:
            self.log(f"Actor {actor.path} doesn't exist, ignoring.", LoggerLevel.ERROR)
        context = self._children[actor.name]
        context._task.cancel()

    @property
    def self(self) -> ActorRef[T]:
        return self._self

    @property
    def system(self) -> "ActorSystem":
        return self._system

    @property
    def children(self) -> Iterable[ActorRef[Any]]:
        return map(lambda x: x.self, self._children.values())

    def get_child(self, name: str) -> ActorRef[Any] | None:
        if name not in self._children:
            return None
        return self._children[name].self

    def ask(
        self,
        actor: ActorRef[U],
        message_func: Callable[[Future], U],
        on_result: Callable[[Any], Any],
        on_error: Callable[[Exception], Any] | None = None,
        timeout: float = 5.0,
    ) -> None:
        loop = asyncio.get_event_loop()
        future = Future.of(loop, timeout).then(on_result).catch(on_error)
        message = message_func(future)
        actor.tell(message)

    async def wait(self) -> None:
        await asyncio.gather(*map(lambda f: f.wait(), self._children.values()))
        await self._task

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    def watch(self, actor: ActorRef[Any]) -> None:
        if self.get_child(actor.name) != actor:
            raise ValueError("Actor is not a child of this actor")
        context = self._children[actor.name]
        context._task.add_done_callback(
            lambda _: self.self.receive_signal(Terminated(actor))
        )

    def log(self, msg: str, level: LoggerLevel = LoggerLevel.INFO) -> None:
        msg = f"{self.self}: {msg}"
        logger = Logger.instance
        if level == LoggerLevel.DEBUG:
            logger.debug(msg)
        elif level == LoggerLevel.INFO:
            logger.info(msg)
        elif level == LoggerLevel.WARNING:
            logger.warning(msg)
        elif level == LoggerLevel.ERROR:
            logger.error(msg)
        elif level == LoggerLevel.CRITICAL:
            logger.error(msg)
            assert False, "Critical error, exiting."
        else:
            raise ValueError("Invalid log level")
