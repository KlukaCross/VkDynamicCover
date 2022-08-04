from PIL import Image


class Widget:
    def __init__(self, config, **kwargs):
        self.vk_session = config.get("vk_session")
        self.app_id = config.get("app_id")
        self.group_id = config.get("group_id")
        self.donate_key = config.get("donate_key")

        self.name = kwargs.get("name", "Widget")
        self.xy = kwargs.get("xy", (0, 0))

    def draw(self, surface: Image) -> Image:
        return surface
