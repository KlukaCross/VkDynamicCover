from PIL import Image


class Widget:
    def __init__(self, **kwargs):
        self.config = kwargs.get("config", {})
        self.vk_session = kwargs.get("vk_session")
        self.name = kwargs.get("name", "widget")
        self.xy = kwargs.get("xy", (0, 0))

    def draw(self, surface: Image) -> Image:
        pass
