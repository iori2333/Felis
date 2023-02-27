from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from felis.adapter import Adapter


class AdapterBackend(ABC):

    def __init__(self, adapter: Adapter) -> None:
        self.adapter = adapter

    @staticmethod
    def of(backend: str, adapter: Adapter) -> "AdapterBackend":
        raise NotImplementedError()
