from enum import Enum
import logging
from pathlib import Path
import sys
from typing_extensions import Self


class LoggerLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Logger:
    _instance: Self | None = None

    def __init__(self) -> None:
        self._logger = logging.getLogger("felis")
        self._logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    @classmethod
    @property
    def instance(cls) -> Self:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def debug(self, msg: str) -> None:
        self._logger.debug(msg)

    def info(self, msg: str) -> None:
        self._logger.info(msg)

    def warning(self, msg: str) -> None:
        self._logger.warning(msg)

    def error(self, msg: str) -> None:
        self._logger.error(msg)

    def set_level(self, level: LoggerLevel) -> None:
        self._logger.setLevel(level.value)

    def add_output(self, path: str | Path) -> None:
        self._logger.addHandler(logging.FileHandler(path))


logger = Logger.instance
