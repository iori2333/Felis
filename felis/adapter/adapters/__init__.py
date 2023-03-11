from ..adapter import Adapter


class AdapterFactory:
    @staticmethod
    def get(name: str) -> Adapter:
        if name == "onebot":
            from .onebot import OneBotAdapter

            return OneBotAdapter()
        else:
            raise ValueError(f"unknown adapter: {name}")
