import random

import typing
from PIL import Image

from .widget import Widget
from VkDynamicCover.utils import DrawTools
from pathlib import Path
from VkDynamicCover.types import Interval, exceptions, Coordinates
from VkDynamicCover.utils import VkTools

from abc import abstractmethod, ABC


class Picture(Widget, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize = kwargs.get("resize")
        self.xy = kwargs.get("xy", [0, 0])

    def draw(self, surface):
        img = self.get_image()
        if not img:
            return surface
        img = self._get_resized_image(img)
        return DrawTools.draw_image(surface=surface, img=img, shift=self._get_shift())

    @property
    def resize(self):
        return self._resize

    @resize.setter
    def resize(self, interval: list):
        if interval and not isinstance(interval, list):
            raise exceptions.CreateTypeException("interval", list, type(interval))
        self._resize = Interval(interval[0], interval[1])

    @property
    def xy(self) -> Coordinates:
        return self._xy

    @xy.setter
    def xy(self, xy: typing.List[int]):
        if not isinstance(xy, list):
            raise exceptions.CreateTypeException("xy", list, type(xy))
        if len(xy) != 2:
            raise exceptions.CreateValueException("xy length", 2, len(xy))
        self._xy = Coordinates(xy[0], xy[1])

    @abstractmethod
    def get_image(self) -> Image:
        raise NotImplementedError

    def _get_resized_image(self, image: Image):
        return DrawTools.get_resized_image(image, self.resize) if self.resize else image

    def _get_shift(self) -> (int, int):
        return self._xy.x, self._xy.y


class LocalPicture(Picture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._path = kwargs.get("path")

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path: str):
        if path and not isinstance(path, str):
            raise exceptions.CreateTypeException("path", str, type(path))
        self._path = path

    def get_image(self) -> Image:
        p = Path(self.path)
        return DrawTools.get_image_from_path(p)


class UrlPicture(Picture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._url = kwargs.get("url")

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url: str):
        if url and not isinstance(url, str):
            raise exceptions.CreateTypeException(f"url", str, type(url))
        self._url = url

    def get_image(self) -> Image:
        return DrawTools.get_image_from_url(self.url)


class RandomPicture(Picture, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.random_formula = kwargs.get("random_formula")
        self._random_function = None
        self.set_random_function()

    @property
    def random_formula(self) -> str:
        return self._random_formula

    @random_formula.setter
    def random_formula(self, random_formula: str):
        if random_formula and not isinstance(random_formula, str):
            raise exceptions.CreateTypeException("random_formula", str, type(random_formula))
        self._random_formula = random_formula

    @abstractmethod
    def get_image(self) -> Image:
        raise NotImplementedError

    def set_random_function(self):
        if not self.random_formula:
            self._random_function = lambda count: random.randint(0, count - 1)
        else:
            pass


class RandomLocalPicture(RandomPicture, LocalPicture):
    def get_image(self):
        return DrawTools.get_random_image_from_dir(path=Path(self.path), rand_func=self._random_function)


class RandomAlbumPicture(RandomPicture, UrlPicture):
    def get_image(self):
        url = VkTools.get_random_image_url(group_id=self.group_id, album_id=self.url, rand_func=self._random_function)
        return DrawTools.get_image_from_url(url)


class VkAvatar(Picture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.crop_type = kwargs.get("crop_Type")
        self.user_id = kwargs.get("user_id")
        self.default_url = kwargs.get("default_url")

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int):
        if user_id and not isinstance(user_id, int):
            raise exceptions.CreateTypeException("user_id", int, type(user_id))
        self._user_id = user_id

    @property
    def crop_type(self) -> str:
        return self._crop_type

    @crop_type.setter
    def crop_type(self, crop_type: str):
        if crop_type and not isinstance(crop_type, str):
            raise exceptions.CreateTypeException("crop_type", str, type(crop_type))
        self._crop_type = crop_type

    @property
    def default_url(self):
        return self._default_url

    @default_url.setter
    def default_url(self, url: str):
        if url and not isinstance(url, str):
            raise exceptions.CreateTypeException(f"url", str, type(url))
        self._default_url = url

    def get_image(self) -> Image:
        user = VkTools.get_user(user_id=self.user_id, fields="crop_photo")

        if "crop_photo" not in user:
            return DrawTools.get_image_from_url(self.default_url)

        sizes = user["crop_photo"]["photo"]["sizes"]
        photo_max = 0
        for i in range(len(sizes)):
            if sizes[i]["width"] > sizes[photo_max]["width"]:
                photo_max = i

        photo = DrawTools.get_image_from_url(sizes[photo_max]["url"])

        if self.crop_type in ["crop", "small"]:
            photo = photo.crop((photo.width * user["crop_photo"]["crop"]["x"] // 100,
                                photo.height * user["crop_photo"]["crop"]["y"] // 100,
                                photo.width * user["crop_photo"]["crop"]["x2"] // 100,
                                photo.height * user["crop_photo"]["crop"]["y2"] // 100))
            if self.crop_type == "small":
                photo = photo.crop((photo.width * user["crop_photo"]["rect"]["x"] // 100,
                                    photo.height * user["crop_photo"]["rect"]["y"] // 100,
                                    photo.width * user["crop_photo"]["rect"]["x2"] // 100,
                                    photo.height * user["crop_photo"]["rect"]["y2"] // 100))
        return photo
