from dataclasses import dataclass
from typing import Any, Mapping


class DriverMessage:
    @staticmethod
    def of_data(data: Mapping[str, Any]) -> "BackendData":
        return BackendData(data)

    @staticmethod
    def of_error(error: Exception) -> "BackendError":
        return BackendError(error)

    @staticmethod
    def of_action(action: Mapping[str, Any]) -> "AdapterAction":
        return AdapterAction(action)

    @staticmethod
    def of_closed() -> "BackendClosed":
        return BackendClosed()


@dataclass
class BackendData(DriverMessage):
    data: Mapping[str, Any]


@dataclass
class BackendError(DriverMessage):
    error: Exception


@dataclass
class BackendClosed(DriverMessage):
    pass


@dataclass
class AdapterAction(DriverMessage):
    action: Mapping[str, Any]
