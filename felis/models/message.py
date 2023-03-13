from typing import Any, Generic, TypeVar, overload
from typing_extensions import Self, override
from pydantic import BaseModel


class MessageData(BaseModel):
    pass


T = TypeVar("T", bound=MessageData)


class Text(MessageData):
    text: str


class Mention(MessageData):
    user_id: str


class MentionAll(MessageData):
    pass


class Image(MessageData):
    file_id: str


class Voice(MessageData):
    file_id: str


class Audio(MessageData):
    file_id: str


class Video(MessageData):
    file_id: str


class File(MessageData):
    file_id: str


class Location(MessageData):
    latitude: float
    longitude: float
    title: str
    address: str


class Reply(MessageData):
    message_id: str
    user_id: str | None


class Extended(MessageData):
    data: dict[str, Any]

    @override
    def dict(self, **kwargs):
        res = super().dict(**kwargs)
        return res["data"]


segment_map = {
    "text": Text,
    "mention": Mention,
    "mention_all": MentionAll,
    "image": Image,
    "voice": Voice,
    "audio": Audio,
    "video": Video,
    "file": File,
    "location": Location,
    "reply": Reply,
}


class MessageSegment(BaseModel, Generic[T]):
    type: str
    data: T

    @staticmethod
    def text(text: str) -> "MessageSegment[Text]":
        return MessageSegment(type="text", data=Text(text=text))

    @staticmethod
    def mention(user_id: str) -> "MessageSegment[Mention]":
        return MessageSegment(type="mention", data=Mention(user_id=user_id))

    @staticmethod
    def mention_all() -> "MessageSegment[MentionAll]":
        return MessageSegment(type="mention_all", data=MentionAll())

    @staticmethod
    def image(file_id: str) -> "MessageSegment[Image]":
        return MessageSegment(type="image", data=Image(file_id=file_id))

    @staticmethod
    def voice(file_id: str) -> "MessageSegment[Voice]":
        return MessageSegment(type="voice", data=Voice(file_id=file_id))

    @staticmethod
    def audio(file_id: str) -> "MessageSegment[Audio]":
        return MessageSegment(type="audio", data=Audio(file_id=file_id))

    @staticmethod
    def video(file_id: str) -> "MessageSegment[Video]":
        return MessageSegment(type="video", data=Video(file_id=file_id))

    @staticmethod
    def file(file_id: str) -> "MessageSegment[File]":
        return MessageSegment(type="file", data=File(file_id=file_id))

    @staticmethod
    def location(
        latitude: float,
        longitude: float,
        title: str,
        address: str,
    ) -> "MessageSegment[Location]":
        return MessageSegment(
            type="location",
            data=Location(
                latitude=latitude,
                longitude=longitude,
                title=title,
                address=address,
            ),
        )

    @staticmethod
    def reply(
        message_id: str,
        user_id: str | None = None,
    ) -> "MessageSegment[Reply]":
        return MessageSegment(
            type="reply",
            data=Reply(message_id=message_id, user_id=user_id),
        )

    @staticmethod
    def of_extended(type: str, data: dict[str, Any]) -> "MessageSegment[Extended]":
        return MessageSegment(type=type, data=Extended(data=data))

    @staticmethod
    def construct_from_dict(type: str, data: dict[str, Any]) -> MessageData:
        if type not in segment_map:
            return Extended(data=data)

        DataClass = segment_map[type]
        return DataClass(**data)

    def __init__(self, **data) -> None:
        if isinstance(data["data"], dict):
            data["data"] = self.construct_from_dict(data["type"], data["data"])
        super().__init__(**data)


class Message(list[MessageSegment]):
    @classmethod
    def of(cls, *segments: MessageSegment | str) -> "Message":
        transformed = [
            MessageSegment.text(segment) if isinstance(segment, str) else segment
            for segment in segments
        ]
        return cls(transformed)

    def as_text(self) -> str:
        return "".join(segment.data.text for segment in self if segment.type == "text")

    def split_first(self, mark: str = " ") -> tuple[str, Self]:
        if not self:
            return "", Message()
        if self[0].type != "text":
            return "", self
        text = self[0].data.text
        splits = text.split(mark, 1)
        if len(splits) == 1:
            return text, self[1:]
        return splits[0], splits[1] + self[1:]

    def split(self, mark: str = " ") -> list[Self]:
        ret = list[Self]()
        current = Message()
        for segment in self:
            if segment.type != "text":
                current.append(segment)
                continue
            for text in segment.data.text.split(mark):
                if not text:
                    continue
                current.add(MessageSegment.text(text))
                ret.append(current)
                current = Message()
        if current:
            ret.append(current)
        return ret

    def add(self, segment: MessageSegment) -> None:
        if not self:
            self.append(segment)
        elif segment.type == "text" and self[-1].type == "text":
            self[-1].data.text += segment.data.text
        else:
            self.append(segment)

    def __iadd__(self, other: str | MessageSegment | Self) -> Self:
        if isinstance(other, MessageSegment):
            self.add(other)
        elif isinstance(other, str):
            if other != "":
                self.add(MessageSegment.text(other))
        else:
            for segment in other:
                self.add(segment)
        return self

    def __add__(self, other: str | MessageSegment | Self) -> Self:
        ret = Message()
        ret += self
        ret += other
        return ret

    def __radd__(self, other: str | MessageSegment | Self) -> Self:
        ret = Message()
        ret += other
        ret += self
        return ret

    @overload
    def __getitem__(self, key: int) -> MessageSegment:
        ...

    @overload
    def __getitem__(self, key: slice) -> Self:
        ...

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Message(super().__getitem__(key))
        return super().__getitem__(key)
