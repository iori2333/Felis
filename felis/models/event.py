from pydantic import BaseModel

from .self import Self


class BaseEvent(BaseModel):
    id: str
    time: float
    type: str
    detail_type: str
    sub_type: str
    self: Self | None

    @property
    def session_id(self) -> str:
        group_id = getattr(self, "group_id", None)
        user_id = getattr(self, "user_id", None)
        session_id = ["felis"]
        if group_id is not None:
            session_id.append(f"g_{group_id}")
        if user_id is not None:
            session_id.append(f"u_{user_id}")
        return ".".join(session_id)
