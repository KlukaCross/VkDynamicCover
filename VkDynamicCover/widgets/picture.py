import random
import typing
from copy import copy

from PIL import Image

from .widget import Widget
from ..utils import draw
from pathlib import Path
from VkDynamicCover.types import Interval
from VkDynamicCover.utils import VkTools

from abc import abstractmethod, ABC


class Picture(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize = kwargs.get("resize")

    def draw(self, surface):
        img = self.get_image()
        if not img:
            return surface
        img = self._get_resized_image(img)
        return draw.draw_image(surface=surface, img=img, shift=self._get_shift())

    @property
    def resize(self):
        return self._resize

    @resize.setter
    def resize(self, interval: Interval):
        self._resize = interval

    @abstractmethod
    def get_image(self) -> Image:
        raise NotImplementedError

    def _get_resized_image(self, image: Image):
        return draw.get_resized_image(image, self.resize) if self.resize else image

    def _get_shift(self) -> (int, int):
        return copy(self.xy)


class LocalPicture(Picture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._path = kwargs.get("path")

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path: str):
        self._path = path

    def get_image(self) -> Image:
        p = Path(self.path)
        return draw.get_image_from_path(p)


class UrlPicture(Picture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._url = kwargs.get("url")

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url: str):
        self._url = url

    def get_image(self) -> Image:
        return draw.get_image_from_url(self.url)


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
        self._random_formula = random_formula

    def set_random_function(self):
        if not self.random_formula:
            self._random_function = lambda count: random.randint(0, count - 1)
        else:
            pass


class RandomLocalPicture(RandomPicture, LocalPicture):
    def get_image(self):
        return draw.get_random_image_from_dir(path=Path(self.path), rand_func=self._random_function)


class RandomAlbumPicture(RandomPicture, UrlPicture):
    def get_image(self):
        url = VkTools.get_random_image_url(group_id=self.group_id, album_id=self.url, rand_func=self._random_function)
        return draw.get_image_from_url(url)


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
        self._user_id = user_id

    @property
    def crop_type(self) -> str:
        return self._crop_type

    @crop_type.setter
    def crop_type(self, crop_type: str):
        self._crop_type = crop_type

    @property
    def default_url(self):
        return self._default_url

    @default_url.setter
    def default_url(self, url: str):
        self._default_url = url

    def get_image(self) -> Image:
        user = VkTools.get_user(user_id=self.user_id, fields="crop_photo")

        if "crop_photo" not in user:
            return draw.get_image_from_url(self.default_url)

        sizes = user["crop_photo"]["photo"]["sizes"]
        photo_max = 0
        for i in range(len(sizes)):
            if sizes[i]["width"] > sizes[photo_max]["width"]:
                photo_max = i

        photo = draw.get_image_from_url(sizes[photo_max]["url"])

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
