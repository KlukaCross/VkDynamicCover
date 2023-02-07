import typing
import uuid

from abc import ABC, abstractmethod
from PIL import Image
from VkDynamicCover.types import exceptions


class WidgetControl(ABC):
    __TYPE__ = "Widget"

    def __init__(self, drawer, designer, info):
        self.__dict__["drawer"] = drawer
        self.__dict__["designer"] = designer
        self.__dict__["info"] = info

    def draw(self, surface: Image) -> Image:
        self.designer.design(self.info)
        return self.drawer.draw(surface, self.info)

    def __getattr__(self, item):
        return getattr(self.info, item)

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
            return
        if hasattr(self.info, key):
            return setattr(self.info, key, value)

    def __str__(self):
        return self.info.name


class WidgetDrawer:
    def draw(self, surface: Image, info: "WidgetInfo") -> Image:
        return surface


class WidgetDesigner:
    def design(self, info: "WidgetInfo"):
        pass


class WidgetInfo:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        if name and not isinstance(name, str):
            raise exceptions.CreateTypeException("name", str, type(name))
        self._name = name if name else str(uuid.uuid4())
