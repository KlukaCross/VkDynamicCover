from .widget import Widget
from .text import Text


class TextSet(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.texts = kwargs.get("texts", [])
        if isinstance(self.texts, dict):
            self.texts = [self.texts]
        for d in self.texts:
            d.setdefault("name", "text")
            d["config"] = self.config

    def draw(self, surface):
        for d in self.texts:
            text = self.get_format_text(d.get("text", ""))
            text_widget = Text(**{**d, "text": text})
            surface = text_widget.draw(surface)
        return surface

    def get_format_text(self, text) -> str:
        return text
