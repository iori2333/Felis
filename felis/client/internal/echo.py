from typing_extensions import override

from ...models.message import Message
from ..command import MessageCommand
from ..register import Commands
from ...models.events import MessageEvent


@Commands.register(name="echo", description="Echo the message back")
class EchoCommand(MessageCommand):
    @override
    async def handle_message(self, event: MessageEvent, message: Message) -> None:
        self.send_back(event, message)
