import json
import os
import os.path as osp
from typing import Mapping, Sequence, Any, Type, TypeVar
from pydantic import BaseModel
import PIL.Image as MImage
from PIL.Image import Image

from ..actor.context import ActorContext

TM = TypeVar("TM", bound=BaseModel)


class ResourceManager:
    def __init__(self, resource_dir: str, context: ActorContext) -> None:
        self.base_dir = resource_dir
        self.context = context
        os.makedirs(self.base_dir, exist_ok=True)

    def json(self, identifier: str) -> dict[str, Any] | list[Any]:
        paths = identifier.split(".")
        resource_path = osp.join(self.base_dir, *paths) + ".json"
        with open(resource_path, "r", encoding="utf8") as f:
            return json.load(f)

    def save_json(
        self,
        model: Mapping[str, Any] | Sequence[Any],
        identifier: str,
        override: bool = False,
    ) -> None:
        save_path = self.resource_dir(identifier) + ".json"
        if not override and osp.exists(save_path):
            return
        try:
            with open(save_path, "w", encoding="utf8") as f:
                json.dump(model, f, indent=4, ensure_ascii=False)
        except Exception as e:
            raise e

    def model(self, identifier: str, model: Type[TM]) -> TM:
        data = self.json(identifier)
        try:
            return model.parse_obj(data)
        except Exception as e:
            raise e

    def save_model(
        self,
        model: BaseModel,
        identifier: str,
        override: bool = True,
    ) -> None:
        self.save_json(model.dict(), identifier, override)

    def image(self, identifier: str, ext: str = ".jpg") -> Image:
        paths = identifier.split(".")
        resource_path = osp.join(self.base_dir, *paths) + ext
        try:
            im = MImage.open(resource_path)
        except Exception as e:
            raise e
        return im

    def resource_dir(self, identifier: str | None = None) -> str:
        path = self.base_dir
        if identifier is not None:
            path = osp.join(path, *identifier.split("."))
        os.makedirs(path, exist_ok=True)
        return osp.abspath(path)
