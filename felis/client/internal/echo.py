from typing_extensions import override

from ..command import Command
from ..register import Commands
from ...models.events import MessageEvent


@Commands.register(name="echo", description="Echo the message back")
class EchoCommand(Command[MessageEvent]):
    @override
    async def execute(self, event: MessageEvent) -> None:
        self.send_back(event, event.message)
