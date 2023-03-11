from typing import TYPE_CHECKING, Callable, Generic, TypeVar
from typing_extensions import Self

if TYPE_CHECKING:
    from .context import ActorContext
from .signals import Signal
from ..utils import cast, LoggerLevel

T = TypeVar("T")
U = TypeVar("U")


class Behavior(Generic[T]):
    def __init__(
        self,
        *,
        apply: "Callable[[ActorContext[T]], Self] | None" = None,
        on_receive: "Callable[[ActorContext[T], T | Signal], Self] | None" = None,
    ) -> None:
        self.apply = apply or (lambda _: self)
        self.on_receive = on_receive or (lambda _, __: self)

    @classmethod
    def from_apply(cls, apply: "Callable[[ActorContext[T]], Self]") -> Self:
        return cls(apply=apply)

    @classmethod
    def from_receive(
        cls, on_receive: "Callable[[ActorContext[T], T | Signal], Self]"
    ) -> Self:
        return cls(on_receive=on_receive)

    @classmethod
    def from_receive_message(
        cls, on_receive: "Callable[[ActorContext[T], T], Self]"
    ) -> Self:
        def _on_receive(context: "ActorContext[T]", msg: T | Signal) -> Self:
            if isinstance(msg, Signal):
                return cls.same
            return on_receive(context, msg)

        return cls(on_receive=_on_receive)

    @classmethod
    def from_receive_signal(
        cls, on_receive: "Callable[[ActorContext[T], Signal], Self]"
    ) -> Self:
        def _on_receive(context: "ActorContext[T]", msg: T | Signal) -> Self:
            if isinstance(msg, Signal):
                return on_receive(context, msg)
            return cls.same

        return cls(on_receive=_on_receive)

    # since Python < 3.12 doesn't support generic function, `Behaviors.same` and `Behaviors.stop`
    # are defined in `Behavior` instead of `Behaviors`.
    @classmethod
    @property
    def same(cls) -> Self:
        return cast[Self](Behaviors.same)

    @classmethod
    @property
    def stop(cls) -> Self:
        return cast[Self](Behaviors.stop)


class Behaviors:
    @staticmethod
    def setup(apply: "Callable[[ActorContext], Behavior[U]]") -> Behavior[U]:
        return Behavior.from_apply(apply)

    @staticmethod
    def receive(
        on_receive: "Callable[[ActorContext, U | Signal], Behavior[U]]",
    ) -> Behavior[U]:
        return Behavior.from_receive(on_receive)

    @staticmethod
    def receive_message(
        on_receive: "Callable[[ActorContext, U], Behavior[U]]",
    ) -> Behavior[U]:
        return Behavior.from_receive_message(on_receive)

    @staticmethod
    def receive_signal(
        on_receive: "Callable[[ActorContext, Signal], Behavior[U]]",
    ) -> Behavior[U]:
        return Behavior.from_receive_signal(on_receive)

    @staticmethod
    def supervise(
        behavior: Behavior[U],
        on_failure: "Callable[[ActorContext, Exception], Behavior[U]]",
        except_type: type[Exception] | tuple[type[Exception], ...] = Exception,
    ) -> Behavior[U]:
        def _on_receive(context: "ActorContext[U]", msg: U | Signal) -> Behavior[U]:
            try:
                return behavior.on_receive(context, msg)
            except except_type as e:
                context.log(
                    f"Supervised actor failed: [exception={e.__class__.__name__},message={e}]",
                    LoggerLevel.ERROR,
                )
                return on_failure(context, e)

        return Behavior.from_receive(_on_receive)

    same = object()
    stop = object()
