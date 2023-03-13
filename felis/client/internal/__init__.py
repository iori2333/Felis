from .echo import EchoCommand
from .ping import PingCommand

internal_commands = [EchoCommand.name, PingCommand.name]

__all__ = [
    "EchoCommand",
    "PingCommand",
]
