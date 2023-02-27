from typing import Generic, TypeVar
from typing_extensions import Self
from pydantic import BaseModel

from .actions import BaseAction, action_map

T = TypeVar('T', bound=BaseAction)


class Action(BaseModel, Generic[T]):
    action: str
    params: T
    echo: str | None

    @classmethod
    def of(cls, action: BaseAction, echo: str | None = None) -> Self:
        return cls(
            action=action_map.get(type(action), "unknown"),
            params=action,
            echo=echo,
        )
