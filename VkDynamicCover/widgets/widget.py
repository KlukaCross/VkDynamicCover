import uuid

from abc import ABC, abstractmethod
from PIL import Image
from VkDynamicCover.types import exceptions


class Widget(ABC):
    def __init__(self, **kwargs):
        self.type = kwargs.get("type")
        self.name = kwargs.get("name")

    @abstractmethod
    def draw(self, surface: Image) -> Image:
        return surface

    def __str__(self):
        return self.name

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, tp: str):
        if not isinstance(tp, str):
            raise exceptions.CreateTypeException("type", str, type(tp))
        self._type = tp

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        if name and not isinstance(name, str):
            raise exceptions.CreateTypeException("name", str, type(name))
        self._name = name if name else uuid.uuid4()

