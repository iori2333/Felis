from typing import Any, TypeVar, Generic

T = TypeVar("T")


class _Cast(Generic[T]):
    def __new__(cls, value: Any) -> T:
        return value


cast = _Cast
