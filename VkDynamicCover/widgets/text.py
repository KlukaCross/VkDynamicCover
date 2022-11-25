from VkDynamicCover.widgets.widget import Widget
from VkDynamicCover.helpers.text_formatting.text_formatter import TextFormatter
from VkDynamicCover.utils import draw
from VkDynamicCover.types import LIMITED_ACTION
import typing


class Text(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text = kwargs.get("text")
        self.font_name = kwargs.get("font_name")
        self.font_size = kwargs.get("font_size")
        self.fill = kwargs.get("fill")
        self.anchor = kwargs.get("anchor")
        self.spacing = kwargs.get("spacing")
        self.direction = kwargs.get("direction")
        self.stroke_width = kwargs.get("stroke_width")
        self.stroke_fill = kwargs.get("stroke_fill")

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


class FormattingText(Text):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._formatter = None

    def get_text(self) -> str:
        return self._formatter.get_format_text()

    @property
    def formatter(self) -> typing.Optional[TextFormatter]:
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: typing.Optional[TextFormatter]):
        if formatter and not isinstance(formatter, TextFormatter):
            raise TypeError
        self._formatter = formatter


class LimitedText(FormattingText):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.limit = kwargs.get("limit")
        self.limit_action = kwargs.get("limit_action")
        self.limit_str = kwargs.get("limit_str")

    def get_text(self) -> str:
        return self._get_formatted_text(super().get_text())

    def _get_formatted_text(self, text):
        if not self.limit or len(text) <= self.limit:
            return text

        res_text = ""
        lines = text.split("\n")
        for line in lines:
            if len(line) > self.limit:
                if self.limit_action == LIMITED_ACTION.DELETE:
                    line = line[:self.limit] + self.limit_str
                elif self.limit_action == LIMITED_ACTION.NEWLINE:
                    line = line[:self.limit - 1] + self.limit_str + "\n" + \
                           self._get_formatted_text(line[self.limit:])
            res_text += line + "\n"

        return res_text[:-1]

    @property
    def limit(self) -> int:
        return self._limit

    @limit.setter
    def limit(self, limit: int):
        self._limit = limit

    @property
    def limit_action(self) -> str:
        return self._limit_action

    @limit_action.setter
    def limit_action(self, action: str):
        self._limit_action = action

    @property
    def limit_str(self) -> str:
        return self._limit_str

    @limit_str.setter
    def limit_str(self, end: str):
        self._limit_str = end


class SpacedText(FormattingText):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw(self, surface):
        pass

    def get_text(self) -> str:
        pass