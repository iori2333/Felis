from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .actor import ActorRef


class Signal:
    pass


class Terminated(Signal):
    def __init__(self, ref: "ActorRef[Any]") -> None:
        self.ref = ref
