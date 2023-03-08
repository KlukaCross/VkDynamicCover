import random
import re

import typing
from abc import ABC, abstractmethod

from PIL import Image

from .widget import WidgetControl, WidgetInfo, WidgetDrawer, WidgetDesigner
from VkDynamicCover.utils import DrawTools
from pathlib import Path
from VkDynamicCover.types import Interval, exceptions, Coordinates
from VkDynamicCover.utils import VkTools


class PictureControl(WidgetControl):
    __TYPE__ = "Picture"


class PictureDrawer(WidgetDrawer):
    def draw(self, surface: Image, info: "PictureInfo") -> Image:
        img = info.image
        if not img:
            return surface
        img = self._get_resized_image(info, img)
        return DrawTools.draw_image(surface=surface, img=img, shift=info.get_shift())

    def _get_resized_image(self, info: "PictureInfo", image: Image):
        return DrawTools.get_resized_image(image, info.resize) if info.resize else image


class PictureDesigner(WidgetDesigner, ABC):
    @abstractmethod
    def design(self, info: "PictureInfo"):
        raise NotImplementedError


class PictureInfo(WidgetInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize = kwargs.get("resize")
        self.xy = kwargs.get("xy", [0, 0])

        self.image = None

    @property
    def resize(self):
        return self._resize

    @resize.setter
    def resize(self, interval: list):
        if not interval:
            self._resize = None
            return
        if not isinstance(interval, list):
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
        self._xy = Coordinates(xy)

    def get_shift(self) -> (int, int):
        return self._xy.x, self._xy.y


class LocalPictureDesigner(PictureDesigner):
    def design(self, info: "LocalPictureInfo"):
        p = Path(info.path)
        info.image = DrawTools.get_image_from_path(p)


class LocalPictureInfo(PictureInfo):
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


class UrlPictureDesigner(PictureDesigner):
    def design(self, info: "UrlPictureInfo"):
        info.image = DrawTools.get_image_from_url(info.url)


class UrlPictureInfo(PictureInfo):
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


class RandomPictureControl(PictureControl):
    __TYPE__ = "RandomPicture"


class RandomPictureDesigner(ABC):
    @staticmethod
    @abstractmethod
    def random_function(pictures_number: int, **kwargs):
        raise NotImplementedError


class RandomLocalPictureDesigner(LocalPictureDesigner, RandomPictureDesigner):
    def design(self, info: "LocalPictureInfo"):
        info.image = DrawTools.get_random_image_from_dir(path=Path(info.path), rand_func=self.random_function)

    @staticmethod
    def random_function(pictures_number: int, **kwargs):
        return random.randint(0, pictures_number)


class RandomAlbumPictureDesigner(UrlPictureDesigner, RandomPictureDesigner):
    ALBUM_REGEX = r"https://(m\.)?vk\.com/album-"

    def design(self, info: "RandomAlbumPictureInfo"):
        group_id, album_id = re.sub(self.ALBUM_REGEX, "", info.url).split('_')
        url = VkTools.get_random_image_from_album(group_id=int(group_id), album_id=int(album_id), user_id=info.user_id,
                                                  rand_func=self.random_function)
        info.image = DrawTools.get_image_from_url(url)

    @staticmethod
    def random_function(pictures_number: int, **kwargs):
        user_id = kwargs.get("user_id")
        return random.randint(0, pictures_number-1) if not user_id else user_id % pictures_number


class RandomAlbumPictureInfo(UrlPictureInfo):
    def __init__(self, **kwargs):
        kwargs["url"] = kwargs.get("album_url")
        super().__init__(**kwargs)
        self._user_id = kwargs.get("user_id")

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int):
        self._user_id = user_id


class VkAvatarControl(PictureControl):
    __TYPE__ = "VkAvatar"


class VkAvatarDesigner(PictureDesigner):
    def design(self, info: "VkAvatarInfo"):
        user = VkTools.get_user(user_id=info.user_id, fields="crop_photo")

        if "crop_photo" not in user:
            return DrawTools.get_image_from_url(info.default_url)

        sizes = user["crop_photo"]["photo"]["sizes"]
        photo_max = 0
        for i in range(len(sizes)):
            if sizes[i]["width"] > sizes[photo_max]["width"]:
                photo_max = i

        photo = DrawTools.get_image_from_url(sizes[photo_max]["url"])

        if info.crop_type in ["crop", "small"]:
            photo = photo.crop((photo.width * user["crop_photo"]["crop"]["x"] // 100,
                                photo.height * user["crop_photo"]["crop"]["y"] // 100,
                                photo.width * user["crop_photo"]["crop"]["x2"] // 100,
                                photo.height * user["crop_photo"]["crop"]["y2"] // 100))
            if info.crop_type == "small":
                photo = photo.crop((photo.width * user["crop_photo"]["rect"]["x"] // 100,
                                    photo.height * user["crop_photo"]["rect"]["y"] // 100,
                                    photo.width * user["crop_photo"]["rect"]["x2"] // 100,
                                    photo.height * user["crop_photo"]["rect"]["y2"] // 100))
        info.image = photo


class VkAvatarInfo(PictureInfo):
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
