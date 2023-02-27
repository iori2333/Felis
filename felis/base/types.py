from typing import Any, Callable, Type, TypeVar

T = TypeVar("T")


class _Cast:

    @staticmethod
    def cast(value: Any) -> Any:
        return value

    def __getitem__(self, _: Type[T]) -> Callable[[Any], T]:
        return self.cast


cast = _Cast()
