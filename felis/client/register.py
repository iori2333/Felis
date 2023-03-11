from typing import Callable, Type
from .command import Command


class Commands:
    registered_commands = dict[str, Type[Command]]()

    @classmethod
    def register(
        cls,
        *,
        name: str,
        aliases: list[str] = [],
        prefix: str | None = "/",
        description: str = "",
    ) -> Callable[[Type[Command]], Type[Command]]:
        def register(command: Type[Command]) -> Type[Command]:
            command.name = name
            command.aliases = aliases
            command.prefix = prefix
            command.description = description
            cls.registered_commands[command.name] = command
            return command

        return register

    @classmethod
    def get(cls, name: str) -> Type[Command] | None:
        return cls.registered_commands.get(name)
