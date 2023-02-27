from pydantic import BaseModel


class Self(BaseModel):
    platform: str
    user_id: str
