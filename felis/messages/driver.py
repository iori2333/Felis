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


class BackendData(DriverMessage):
    def __init__(self, data: Mapping[str, Any]) -> None:
        self.data = data


class BackendError(DriverMessage):
    def __init__(self, error: Exception) -> None:
        self.error = error


class BackendClosed(DriverMessage):
    pass


class AdapterAction(DriverMessage):
    def __init__(self, action: Mapping[str, Any]) -> None:
        self.action = action
