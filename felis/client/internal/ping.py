from typing_extensions import override

from ..register import Commands
from ..command import MessageCommand
from ...models.message import Message
from ...models.events import MessageEvent


@Commands.register(name="ping", description="Ping the bot")
class PingCommand(MessageCommand):
    @override
    async def handle_message(self, event: MessageEvent, _: Message) -> None:
        self.send_back(event, Message.of("Pong!"))
