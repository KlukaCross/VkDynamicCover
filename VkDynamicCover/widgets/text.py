from VkDynamicCover.widgets.widget import Widget
from VkDynamicCover.helpers.text_formatting.text_formatter import TextFormatter
from VkDynamicCover.utils import draw
from VkDynamicCover.types import LIMITED_ACTION
import typing


class Text(Widget):
    def __init__(self):
        super().__init__()

        self._text = ""

        self._font_name = None
        self._font_size = 0

        self._fill = None
        self._anchor = None
        self._spacing = 4
        self._direction = None
        self._stroke_width = 0
        self._stroke_fill = None

        self._formatter = None

    def draw(self, surface):
        text = self.get_text()
        draw.draw_text(surface=surface, text=text, font_name=self.font_name, font_size=self.font_size,
                       fill=self.fill, xy=self.xy, anchor=self.anchor, spacing=self.spacing,
                       direction=self.direction, stroke_width=self.stroke_width,
                       stroke_fill=self.stroke_fill)
        return surface

    def get_text(self) -> str:
        return self.text

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text

    @property
    def font_name(self) -> str:
        return self._font_name

    @font_name.setter
    def font_name(self, font_name: str):
        self._font_name = font_name

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, font_size: int):
        self._font_size = font_size

    @property
    def fill(self) -> str:
        return self._text

    @fill.setter
    def fill(self, fill: str):
        self._fill = fill

    @property
    def anchor(self) -> str:
        return self._anchor

    @anchor.setter
    def anchor(self, anchor: str):
        self._anchor = anchor

    @property
    def spacing(self) -> int:
        return self._spacing

    @spacing.setter
    def spacing(self, spacing: int):
        self._spacing = spacing

    @property
    def direction(self) -> str:
        return self._direction

    @direction.setter
    def direction(self, direction: str):
        self._direction = direction

    @property
    def stroke_width(self) -> int:
        return self._stroke_width

    @stroke_width.setter
    def stroke_width(self, stroke_width: int):
        self._stroke_width = stroke_width

    @property
    def stroke_fill(self) -> int:
        return self._stroke_fill

    @stroke_fill.setter
    def stroke_fill(self, stroke_fill: int):
        self._stroke_fill = stroke_fill

    @property
    def formatter(self) -> typing.Optional[TextFormatter]:
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: typing.Optional[TextFormatter]):
        if formatter and not isinstance(formatter, TextFormatter):
            raise TypeError
        self._formatter = formatter


class LimitedText(Text):
    def __init__(self):
        super().__init__()
        self._max = None
        self._action = LIMITED_ACTION.NONE
        self._end = ""

    def get_text(self) -> str:
        return self.get_formatted_text(self.text)

    def get_formatted_text(self, text):
        if not self.max or len(text) <= self.max:
            return text

        res_text = ""
        lines = text.split("\n")
        for line in lines:
            if len(line) > self.max:
                if self.action == LIMITED_ACTION.DELETE:
                    line = line[:self.max] + self.end
                elif self.action == LIMITED_ACTION.NEWLINE:
                    line = line[:self.max-1] + self.end + "\n" + \
                           self.get_formatted_text(line[self.max:])
            res_text += line + "\n"

        return res_text[:-1]

    @property
    def max(self) -> int:
        return self._max

    @max.setter
    def max(self, max: int):
        self._max = max

    @property
    def action(self) -> str:
        return self._action

    @action.setter
    def action(self, action: str):
        self._action = action

    @property
    def end(self) -> str:
        return self._end

    @end.setter
    def end(self, end: str):
        self._end = end
