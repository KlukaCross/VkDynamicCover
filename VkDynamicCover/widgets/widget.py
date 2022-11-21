import typing
from PIL import Image
from VkDynamicCover.types import Coordinates


class Widget:
    def __init__(self):
        self.group_id = 0

        self._type = None
        self._name = None
        self._xy = None

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
            raise ValueError("group id must be numeric")
        self._group_id = group_id

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, tp: str):
        self._type = tp

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def xy(self) -> Coordinates:
        return self._xy

    @xy.setter
    def xy(self, xy: typing.List[int]):
        if not isinstance(xy, list):
            raise TypeError("xy must be list")
        if len(xy) != 2:
            raise ValueError("xy length must be 2")
        self._xy = Coordinates(xy[0], xy[1])
