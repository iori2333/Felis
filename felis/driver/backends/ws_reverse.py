import asyncio
import json
import websockets.client as wsc
from typing import Any, Callable, Coroutine, Mapping
from websockets.exceptions import ConnectionClosed

from ..backend import Backend, Backends
from ..actor import DriverMessage
from ...actor import ActorRef


@Backends.register("websocket_reverse")
class WebsocketReverseBackend(Backend):
    def __init__(
        self,
        driver_actor: "ActorRef[DriverMessage]",
        url: str,
        access_token: str | None,
    ) -> None:
        super().__init__(driver_actor, url, access_token)
        self.requests = asyncio.Queue[Mapping[str, Any]]()

    async def on_message(self, data: str | bytes) -> None:
        data_dict = json.loads(data)
        if not isinstance(data_dict, dict):
            self.on_error(ValueError(f"invalid data: {data_dict}"))
        self.driver.tell(DriverMessage.of_data(data_dict))

    def on_error(self, e: Exception) -> None:
        self.driver.tell(DriverMessage.of_error(e))

    def on_closed(self) -> None:
        self.driver.tell(DriverMessage.of_closed())

    async def start(self) -> None:
        try:
            async with wsc.connect(self.url, extra_headers=self.get_headers()) as ws:
                await asyncio.gather(
                    self.task(ws, self._send),
                    self.task(ws, self._recv),
                    return_exceptions=True,
                )
        except ConnectionError:
            self.on_closed()

    async def task(
        self,
        ws: wsc.WebSocketClientProtocol,
        handler: Callable[[wsc.WebSocketClientProtocol], Coroutine[Any, Any, None]],
    ) -> None:
        while True:
            try:
                await handler(ws)
            except ConnectionClosed:
                self.on_closed()
                return
            except Exception as e:
                self.on_error(e)
            except asyncio.CancelledError:
                return

    async def _send(self, ws: wsc.WebSocketClientProtocol) -> None:
        request = await self.requests.get()
        data = json.dumps(request)
        await ws.send(data)

    async def _recv(self, ws: wsc.WebSocketClientProtocol) -> None:
        data = await ws.recv()
        await self.on_message(data)

    def send(self, request: Mapping[str, Any]) -> None:
        self.requests.put_nowait(request)

    def get_headers(self) -> Mapping[str, str]:
        headers = {}
        if self.access_token is not None:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
