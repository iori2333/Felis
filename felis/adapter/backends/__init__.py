from typing import Type
from ..adapter import Adapter
from .base import BaseBackend, ResponseConverter


class BackendFactory:

    @staticmethod
    def of(
        backend_type: str,
        self: Adapter,
        converter: Type[ResponseConverter],
    ) -> BaseBackend:
        raise NotImplementedError()
