import asyncio
from typing import Callable, Generic, TypeVar
from typing_extensions import Self

from ..utils import logger

T = TypeVar("T")


class Future(Generic[T]):
    def __init__(self, future: asyncio.Future, timeout: float) -> None:
        self._future = future
        self._done_callbacks: list[Callable[[T], None]] = []
        self._error_callbacks: list[Callable[[Exception], None]] = []
        if timeout > 0:
            future.get_loop().call_later(timeout, lambda: self.cancel())
        self._future.add_done_callback(lambda _: self.on_done())

    @classmethod
    def of(cls, loop: asyncio.AbstractEventLoop, timeout: float) -> Self:
        future = loop.create_future()
        return cls.from_future(future, timeout)

    @classmethod
    def from_future(cls, future: asyncio.Future, timeout: float) -> Self:
        return cls(future, timeout)

    def set_result(self, result: T) -> None:
        if self._future.done():
            return
        self._future.set_result(result)

    def set_exception(self, exception: Exception) -> None:
        if self._future.done():
            return
        self._future.set_exception(exception)

    def on_done(self):
        try:
            result = self._future.result()
        except asyncio.CancelledError as e:
            logger.error(f"Future cancelled: {e}")
        except Exception as e:
            for callback in self._error_callbacks:
                callback(e)
        else:
            for callback in self._done_callbacks:
                callback(result)

    def then(self, callback: Callable[[T], None] | None) -> Self:
        if callback is not None:
            self._done_callbacks.append(callback)
        return self

    def catch(self, callback: Callable[[Exception], None] | None) -> Self:
        if callback is not None:
            self._error_callbacks.append(callback)
        return self

    def cancel(self):
        self._future.set_exception(asyncio.TimeoutError())
