from .widget import Widget
from ..utils import draw


class Text(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get("text", "")

        font = kwargs.get("font", {}) or {}
        main_font = self.config.get("main_font", {}) or {}
        self.font_name = font.get("name") or main_font.get("name")
        self.font_size = font.get("size") or main_font.get("size")

        self.fill = kwargs.get("fill", None)
        self.anchor = kwargs.get("anchor", None)
        self.spacing = kwargs.get("spacing", 4)
        self.direction = kwargs.get("direction", None)
        self.stroke_width = kwargs.get("stroke_width", 0)
        self.stroke_fill = kwargs.get("stroke_fill", None)

    def draw(self, surface):
        text = self.get_text()
        draw.draw_text(surface=surface, text=text, font_name=self.font_name, font_size=self.font_size,
                       fill=self.fill, xy=self.xy, anchor=self.anchor, spacing=self.spacing,
                       direction=self.direction, stroke_width=self.stroke_width,
                       stroke_fill=self.stroke_fill)
        return surface

    def get_text(self) -> str:
        return self.text
