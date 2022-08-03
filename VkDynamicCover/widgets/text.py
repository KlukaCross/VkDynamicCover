from .widget import Widget
from ..utils import draw


class Text(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text = kwargs.get("text", "")

        self.font_name = kwargs.get("font", {}).get("name")
        self.font_size = kwargs.get("font", {}).get("font")

        self.fill = kwargs.get("fill", None)
        self.anchor = kwargs.get("anchor", None)
        self.spacing = kwargs.get("spacing", 4)
        self.direction = kwargs.get("direction", None)
        self.stroke_width = kwargs.get("stroke_width", 0)
        self.stroke_fill = kwargs.get("stroke_fill", None)

        limit = kwargs.get("limit", {})
        self.limit = Limit(**limit)

    def draw(self, surface):
        text = self.get_text()
        text = self.limit.get_format_text(text)
        draw.draw_text(surface=surface, text=text, font_name=self.font_name, font_size=self.font_size,
                       fill=self.fill, xy=self.xy, anchor=self.anchor, spacing=self.spacing,
                       direction=self.direction, stroke_width=self.stroke_width,
                       stroke_fill=self.stroke_fill)
        return surface

    def get_text(self) -> str:
        return self.text


class Limit:
    def __init__(self, **kwargs):
        self.max = kwargs.get("max", None)
        self.action = kwargs.get("action", None)
        self.end = kwargs.get("end", "")

    def get_format_text(self, text):
        if not self.max or len(text) <= self.max:
            return text

        res_text = ""
        lines = text.split("\n")
        for line in lines:
            if len(line) > self.max:
                if self.action == "delete":
                    line = line[:self.max] + self.end
                elif self.action == "newline":
                    line = line[:self.max-1] + self.end + "\n" + \
                           self.get_format_text(line[self.max:])
            res_text += line + "\n"

        return res_text[:-1]
