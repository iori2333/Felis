from pydantic import BaseModel
from typing_extensions import Self

class BaseEvent(BaseModel):
    id: str
    time: float
    type: str
    detail_type: str
    sub_type: str
    self: Self | None
