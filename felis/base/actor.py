from abc import ABC, abstractmethod
import asyncio
from asyncio import AbstractEventLoop, Future
from asyncio.queues import Queue
import os
from typing import TYPE_CHECKING, Callable, Coroutine, Generic, Type, TypeVar, Any
from .types import cast

from typing_extensions import Self

if TYPE_CHECKING:
    from .system import ActorSystem

T = TypeVar("T")  # actor receive type
U = TypeVar("U")
E = TypeVar("E", bound=Exception)  # error type


class Message(Generic[T]):

    def __init__(self, payload: T, future: Future | None) -> None:
        self.payload = payload
        self.future = future

    @classmethod
    def of(cls, payload: T, future: Future | None = None) -> Self:
        return cls(payload, future)


class Behavior(Generic[T]):

    def __init__(
        self,
        behavior: Callable[[Message[T]], Coroutine[Any, Any, Self]],
    ) -> None:
        self.apply = behavior

    @classmethod
    def of(
        cls,
        apply: Callable[[Message[T]], Coroutine[Any, Any, Self]],
    ) -> Self:
        return cls(apply)

    @classmethod
    def supervise(
        cls,
        behavior: Callable[[Message[T]], Coroutine[Any, Any, Self]],
        on_errors: Callable[[Exception], Coroutine[Any, Any, Self]],
        errors: Type[Exception] | tuple[Type[Exception], ...] = Exception,
    ) -> Self:

        async def apply(message: Message[T]) -> Self:
            try:
                return await behavior(message)
            except errors as e:
                return await on_errors(e)

        return cls(apply)

    async def __call__(self, message: Message[T]) -> Self:
        return await self.apply(message)

    # special behaviors, use cast to avoid lint error
    SAME = cast[Self](object())
    STOP = cast[Self](object())


class ActorContext:

    def __init__(
        self,
        system: "ActorSystem",
        parent: "Actor | None",
        event_loop: AbstractEventLoop,
    ) -> None:
        self.system = system
        self.parent = parent
        self.children = dict[str, "Actor"]()
        self.event_loop = event_loop

    @classmethod
    def of(
        cls,
        system: "ActorSystem",
        event_loop: AbstractEventLoop,
        parent: "Actor | None" = None,
    ) -> Self:
        return cls(system, parent, event_loop)

    def copy_of(
        self,
        *,
        system: "ActorSystem | None" = None,
        parent: "Actor | None" = None,
        event_loop: AbstractEventLoop | None = None,
    ) -> Self:
        return ActorContext(
            system or self.system,
            parent or self.parent,
            event_loop or self.event_loop,
        )


class Actor(ABC, Generic[T]):

    def __init__(
        self,
        name: str,
        context: ActorContext,
    ) -> None:
        self.name = name
        if context.parent is None:
            self.path = os.sep + name
        else:
            self.path = os.path.join(context.parent.path, name)
        self.context = context

        self._mailbox = Queue[Message[T]]()
        self._task = context.event_loop.create_task(self.run())

    @classmethod
    def of(
        cls,
        name: str,
        context: ActorContext,
    ) -> Self:
        return cls(name, context)

    async def run(self) -> None:
        try:
            state = await self.apply()
            while state is not Behavior.STOP:
                message = await self._mailbox.get()
                next_state = await state(message)
                self._mailbox.task_done()
                if next_state is Behavior.STOP:
                    return
                if next_state is not Behavior.SAME:
                    state = next_state
        except asyncio.CancelledError:
            return

    async def tell(self, to: "Actor[U]", message: U) -> None:
        await to._put(Message.of(message))

    async def ask(
        self,
        to: "Actor[U]",
        message: U,
        timeout: int | None = None,
    ) -> Any:
        future = asyncio.Future()

        await to._put(Message.of(message, future))
        if timeout is not None:
            return await asyncio.wait_for(future, timeout)
        return await future

    async def _put(self, message: Message[T]) -> None:
        if self._task.done():
            raise RuntimeError(f"actor {self.path} is already stopped")
        await self._mailbox.put(message)

    def spawn(self, name: str, actorType: "Type[Actor[U]]") -> "Actor[U]":
        if name in self.context.children:
            raise ValueError(f"child {name} already exists")
        new_context = self.context.copy_of(parent=self)
        child = actorType.of(name, new_context)
        self.context.children[name] = child
        return child

    async def stop(self) -> None:
        await self._task
        await self._mailbox.join()
        for child in self.context.children.values():
            await child.stop()
        if not self._mailbox.empty():
            raise RuntimeWarning(
                f"[{self.path}] {self._mailbox.qsize()} messages are not processed"
            )

    @abstractmethod
    async def apply(self) -> Behavior[T]:
        raise NotImplementedError
