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
            p = Path(self.path)
            if not p.is_dir():
                logger.warning(f"{p} не является директорией")
                return
            lst = list(filter(lambda x: x.suffix in [".png", ".jpg", ".jpeg", ".gif"], p.glob("*.*")))
            rand_pic_path = random.choice(lst)
            return draw.get_image_from_path(rand_pic_path)
        if self.group_id and self.album_id:
            url = vk.get_random_picture_url(vk_session=self.vk_session, group_id=self.group_id, album_id=self.album_id)
            return draw.get_image_from_url(url)
