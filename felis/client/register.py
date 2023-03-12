from typing import Callable, Type
from typing_extensions import override

from .command import Command
from ..utils import Registry


class Commands(Registry[Command]):
    @override
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
            cls.registries[command.name] = command
            return command

        return register
