from abc import abstractmethod
from asyncio import Future
from typing import Any
from typing_extensions import override

from ..models.action import Action, BaseAction
from .base import BaseBackend


class FutureActions:

    def __init__(self) -> None:
        self.seq = 0
        self.actions = dict[str, Future]()

    def next(self) -> tuple[str, Future]:
        self.seq += 1
        seq = str(self.seq)
        future = Future()
        self.actions[seq] = future
        return str(seq), future

    def get(self, seq: str) -> Future:
        return self.actions[seq]

    def set_result(self, seq: str, data: Any) -> None:
        future = self.actions.pop(seq)
        future.set_result(data)


futures = FutureActions()


class WebSocketBackend(BaseBackend):

    @abstractmethod
    async def send(self, data: Any) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def recv(self) -> Any:
        raise NotImplementedError()

    @override
    async def call_api(self, action: BaseAction) -> Any:
        seq, future = futures.next()
        action_req = Action.of(action, seq)
        await self.send(action_req.json())
        return await future
