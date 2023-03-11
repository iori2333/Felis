from typing import Generic, TypeVar
from typing_extensions import Self
from pydantic import BaseModel

from .actions import action_map

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R", bound=BaseModel)


class Action(BaseModel, Generic[T]):
    action: str
    params: T
    echo: str | None

    @classmethod
    def of(cls, action: T, echo: str | None = None) -> Self:
        return cls(
            action=action_map.get(type(action), "unknown"),
            params=action,
            echo=echo,
        )


class ActionResponse(BaseModel, Generic[R]):
    status: str
    retcode: int
    data: R
    message: str
    echo: str | None
