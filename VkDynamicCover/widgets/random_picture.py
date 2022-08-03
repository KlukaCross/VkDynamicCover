import random
from pathlib import Path

from loguru import logger

from ..utils import draw, vk
from .picture import Picture


class RandomPicture(Picture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.group_id = kwargs.get("group_id") or self.config["group_id"]
        self.album_id = kwargs.get("album_id")

    def get_image(self):
        if self.path:
            return draw.get_random_image_from_dir(self.path)
        if self.group_id and self.album_id:
            url = vk.get_random_image_url(vk_session=self.vk_session, group_id=self.group_id, album_id=self.album_id)
            return draw.get_image_from_url(url)
