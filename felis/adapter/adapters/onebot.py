from typing import Any, Mapping, Type
from typing_extensions import override
from pydantic import BaseModel

from ..adapter import Adapter, Adapters
from ...models.action import ActionResponse
from ...models.actions import response_map
from ...models.event import BaseEvent, UnknownEvent
from ...models.events import event_map


@Adapters.register("onebot")
class OneBotAdapter(Adapter):
    @override
    def is_response(self, data: Mapping[str, Any]) -> bool:
        return data.get("echo") is not None

    @override
    def create_action_response(
        self, data: Mapping[str, Any], action_type: Type[BaseModel]
    ) -> ActionResponse:
        copy = dict(data)
        del copy["echo"]
        actual_data = copy["data"]
        if action_type in response_map:
            ResponseType = response_map[action_type]
            if isinstance(ResponseType, tuple):
                ContainerType, ValueType = ResponseType
                container = ContainerType()
                for value in actual_data:
                    if isinstance(value, dict):
                        container.add(ValueType(**value))
                    else:
                        container.add(ValueType(value))
                copy["data"] = container
            else:
                copy["data"] = ResponseType(**data["data"])
        else:
            copy["data"] = None
        return ActionResponse(**copy)

    @override
    def create_event(self, data: Mapping[str, Any]) -> BaseEvent:
        detail = data["detail_type"]
        if detail not in event_map:
            event = UnknownEvent.parse_obj(data)
            event.data = dict(data)
            return event
        EventType = event_map[detail]
        return EventType(**data)
