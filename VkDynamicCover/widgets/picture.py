from copy import copy

from PIL import Image

from .widget import Widget
from ..utils import draw
from pathlib import Path


class Picture(Widget):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.path = kwargs.get("path", None)
        self.url = kwargs.get("url", None)
        self.resize = kwargs.get("resize", None)

    def draw(self, surface):
        img = self.get_image()
        if not img:
            return surface
        img = self.get_resized_image(img)
        return draw.draw_image(surface=surface, img=img, shift=self.get_shift())

    def get_image(self) -> Image:
        if self.path:
            p = Path(self.path)
            return draw.get_image_from_path(p)
        if self.url:
            return draw.get_image_from_url(self.url)

    def get_resized_image(self, image: Image):
        return draw.get_resized_image(image, self.resize) if self.resize else image

    def get_shift(self) -> (int, int):
        return copy(self.xy)
