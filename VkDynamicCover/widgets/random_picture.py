import random
from pathlib import Path

from ..utils import draw, vk
from .picture import Picture


class RandomPicture(Picture):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.random_function = kwargs.get("random_function", lambda count: random.randint(0, count-1))
        self.group_id = kwargs.get("group_id") or self.group_id
        self.album_id = kwargs.get("album_id")

    def get_image(self):
        if self.path:
            return draw.get_random_image_from_dir(path=Path(self.path), rand_func=self.random_function)
        if self.group_id and self.album_id:
            url = vk.get_random_image_url(vk_session=self.vk_session, group_id=self.group_id, album_id=self.album_id,
                                          rand_func=self.random_function)
            return draw.get_image_from_url(url)
