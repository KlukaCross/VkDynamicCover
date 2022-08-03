from .widget import Widget

from ..utils import widgets


class TextSet(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

        texts_raw = kwargs.get("texts", [])
        default_args = kwargs.get("default_args", {})

        self.text_widgets = []
        self.texts = []

        for d in texts_raw:
            if isinstance(d, str):
                d = {"text": d}
            d.setdefault("name", "text")
            d = {**default_args, **d}

            self.text_widgets.append(widgets.create_widget(**d))
            self.texts.append(d["text"])

    def draw(self, surface):
        for i in range(len(self.texts)):
            self.text_widgets[i].text = self.get_format_text(self.texts[i])
            surface = self.text_widgets[i].draw(surface)
        return surface

    def get_format_text(self, text) -> str:
        return text
