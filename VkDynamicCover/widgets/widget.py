from PIL import Image


class Widget:
    def __init__(self, **kwargs):
        self.vk_session = kwargs.get("vk_session")
        self.app_id = kwargs.get("app_id")
        self.group_id = kwargs.get("group_id")
        self.donate_key = kwargs.get("donate_key")

        self.name = kwargs.get("name", "widget")
        self.xy = kwargs.get("xy", (0, 0))

    def draw(self, surface: Image) -> Image:
        return surface
