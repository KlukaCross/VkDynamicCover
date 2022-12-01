import typing
import uuid

from PIL import Image
from VkDynamicCover.types import Coordinates
from VkDynamicCover.types import exceptions


class Widget:
    def __init__(self, **kwargs):
        self.group_id = kwargs.get("group_id")

        self.type = kwargs.get("type")
        self.name = kwargs.get("name")

    def draw(self, surface: Image) -> Image:
        return surface

    def __str__(self):
        return self.name

    @property
    def group_id(self) -> int:
        return self._group_id

    @group_id.setter
    def group_id(self, group_id: typing.Union[str, int]):
        if not group_id.isnumeric():
            raise exceptions.CreateTypeException("group_id must be numeric")
        self._group_id = group_id

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, tp: str):
        if not isinstance(tp, str):
            raise exceptions.CreateTypeException(f"type must be str, not {type(tp)}")
        self._type = tp

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        if name and not isinstance(name, str):
            raise exceptions.CreateTypeException(f"name must be str, not {type(name)}")
        self._name = name if name else uuid.uuid4()

