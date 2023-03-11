from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .actor import ActorRef


class Signal:
    def __repr__(self) -> str:
        fields = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}[{fields}]"


class Terminated(Signal):
    def __init__(self, ref: "ActorRef[Any]") -> None:
        self.ref = ref
