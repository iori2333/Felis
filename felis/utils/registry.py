from typing import AnyStr, Callable, Mapping, TypeVar, Generic, Dict, Type, Any

T = TypeVar("T")


class Registry(Generic[T]):
    registries: dict[str, Type[T]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[Type[T]], Type[T]]:
        def init(obj: Type[T]) -> Type[T]:
            cls.registries[name] = obj
            return obj

        return init

    @classmethod
    def get(cls, name: str) -> Type[T] | None:
        return cls.registries.get(name)

    @classmethod
    def get_all(cls) -> Mapping[str, Type[T]]:
        return cls.registries
