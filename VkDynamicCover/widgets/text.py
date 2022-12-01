from functools import reduce

from VkDynamicCover.types.spaced_types import SPACED_TYPES
from VkDynamicCover.widgets.widget import Widget
from VkDynamicCover.helpers.text_formatting.text_formatter import TextFormatter
from VkDynamicCover.utils import DrawTools
from VkDynamicCover.types import LIMITED_ACTION, exceptions, Coordinates
import re
import typing


DEFAULT_FONT_SIZE = 10
DEFAULT_SPACING = 4


class Text(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text = kwargs.get("text")
        self.xy = kwargs.get("xy")
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
        DrawTools.draw_text(surface=surface, text=text, font_name=self.font_name, font_size=self.font_size,
                       fill=self.fill, xy=(self.xy.x, self.xy.y), anchor=self.anchor, spacing=self.spacing,
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
        if text and not isinstance(text, str):
            raise exceptions.CreateTypeException(f"text must be str, not {type(text)}")
        self._text = text if text else ""

    @property
    def font_name(self) -> str:
        return self._font_name

    @font_name.setter
    def font_name(self, font_name: str):
        if font_name and not isinstance(font_name, str):
            raise exceptions.CreateTypeException(f"font_name must be str, not {type(font_name)}")
        self._font_name = font_name

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, font_size: int):
        if font_size and not isinstance(font_size, int):
            raise exceptions.CreateTypeException(f"font_size must be int, not {type(font_size)}")
        self._font_size = font_size if font_size else DEFAULT_FONT_SIZE

    @property
    def fill(self) -> str:
        return self._text

    @fill.setter
    def fill(self, fill: str):
        if fill and not isinstance(fill, str):
            raise exceptions.CreateTypeException(f"fill must be str, not {type(fill)}")
        self._fill = fill

    @property
    def anchor(self) -> str:
        return self._anchor

    @anchor.setter
    def anchor(self, anchor: str):
        if anchor and not isinstance(anchor, str):
            raise exceptions.CreateTypeException(f"anchor must be str, not {type(anchor)}")
        self._anchor = anchor

    @property
    def spacing(self) -> int:
        return self._spacing

    @spacing.setter
    def spacing(self, spacing: int):
        if spacing and not isinstance(spacing, int):
            raise exceptions.CreateTypeException(f"spacing must be int, not {type(spacing)}")
        self._spacing = spacing if spacing else DEFAULT_SPACING

    @property
    def direction(self) -> str:
        return self._direction

    @direction.setter
    def direction(self, direction: str):
        if direction and not isinstance(direction, str):
            raise exceptions.CreateTypeException(f"direction must be str, not {type(direction)}")
        self._direction = direction

    @property
    def stroke_width(self) -> int:
        return self._stroke_width

    @stroke_width.setter
    def stroke_width(self, stroke_width: int):
        if stroke_width and not isinstance(stroke_width, int):
            raise exceptions.CreateTypeException(f"stroke_width must be int, not {type(stroke_width)}")
        self._stroke_width = stroke_width

    @property
    def stroke_fill(self) -> int:
        return self._stroke_fill

    @stroke_fill.setter
    def stroke_fill(self, stroke_fill: int):
        if stroke_fill and not isinstance(stroke_fill, int):
            raise exceptions.CreateTypeException(f"stroke_fill must be int, not {type(stroke_fill)}")
        self._stroke_fill = stroke_fill

    @property
    def xy(self) -> Coordinates:
        return self._xy

    @xy.setter
    def xy(self, xy: typing.List[int]):
        if not isinstance(xy, list):
            raise exceptions.CreateTypeException(f"xy must be list, not {type(xy)}")
        if not xy:
            xy = [0, 0]
        if len(xy) != 2:
            raise exceptions.CreateValueException("xy length must be 2")
        self._xy = Coordinates(xy[0], xy[1])


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
            raise exceptions.CreateTypeException(f"formatter must be TextFormatter, not {type(formatter)}")
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
        if limit and not isinstance(limit, int):
            raise exceptions.CreateTypeException(f"limit must be int, not {type(limit)}")
        self._limit = limit

    @property
    def limit_action(self) -> str:
        return self._limit_action

    @limit_action.setter
    def limit_action(self, limit_action: str):
        if limit_action and not isinstance(limit_action, str):
            raise exceptions.CreateTypeException("limit_action must be str, not {type(spaced_type)}")
        names = [i.name.lower() for i in list(LIMITED_ACTION)]
        if limit_action not in names:
            raise exceptions.CreateValueException(f"limit_action must be one of the {names}")
        self._limit_action = limit_action

    @property
    def limit_str(self) -> str:
        return self._limit_str

    @limit_str.setter
    def limit_str(self, limit_str: str):
        if limit_str and not isinstance(limit_str, str):
            raise exceptions.CreateTypeException("limit_str must be str, not {type(spaced_type)}")
        self._limit_str = limit_str


class SpacedText(FormattingText):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spaced_type = kwargs.get("spaced_type")

    def draw(self, surface):
        def draw_text(txt):
            if self.spaced_type == SPACED_TYPES.PRE_FORM:
                txt = self.formatter.get_format_text(txt)
            DrawTools.draw_text(surface=surface, text=txt, font_name=self.font_name, font_size=self.font_size,
                                fill=self.fill, xy=(self.xy.x + shift_xy[0], self.xy.y + shift_xy[1]), anchor=self.anchor,
                                spacing=self.spacing,
                                direction=self.direction, stroke_width=self.stroke_width,
                                stroke_fill=self.stroke_fill)
        text = self.formatter.get_format_text(self.text) if self.spaced_type == SPACED_TYPES.POST_FORM else self.text
        v_match = re.findall(r'\[vspace\(\d+\)]', text)
        h_match = re.findall(r'\[hspace\(\d+\)]', text)
        shift_xy = [0, 0]
        ind = 0
        from_ind = 0
        v = h = 0
        while v < len(v_match) and h < len(h_match):
            v_ind = text.find(v_match[v], __start=ind)
            h_ind = text.find(h_match[h], __start=ind)
            ind = min(v_ind, h_ind)
            draw_text(text[from_ind:ind])
            if ind == v_ind:
                v += 1
                shift_xy[1] += len(re.match(r'\d+', v_match[v]).group(0))  # todo: добавить len_keys по y
                from_ind = ind + len(v_match[v])
            else:
                h += 1
                shift_xy[0] += len(re.match(r'\d+', h_match[h]).group(0)) - self._len_keys(text[from_ind:ind])
                from_ind = ind + len(h_match[v])

        while v < len(v_match):
            v_ind = text.find(v_match[v], __start=ind)
            ind = v_ind
            draw_text(text[from_ind:ind])
            v += 1
            shift_xy[1] += len(re.match(r'\d+', v_match[v]).group(0))
            from_ind = ind + len(v_match[v])

        while h < len(h_match):
            h_ind = text.find(h_match[h], __start=ind)
            ind = h_ind
            draw_text(text[from_ind:ind])
            h += 1
            shift_xy[0] += len(re.match(r'\d+', h_match[h]).group(0)) - self._len_keys(text[from_ind:ind])
            from_ind = ind + len(h_match[h])

    def _len_keys(self, text: str) -> int:
        match = re.search(r'\{.*}', text)
        res = 0
        if not match:
            return res
        reduce(lambda x: len(x), match.groups(), res)
        return res

    @property
    def spaced_type(self) -> str:
        return self._spaced_type

    @spaced_type.setter
    def spaced_type(self, spaced_type: str):
        if spaced_type and not isinstance(spaced_type, str):
            raise exceptions.CreateTypeException(f"spaced_type must be str, not {type(spaced_type)}")
        names = [i.name.lower() for i in list(SPACED_TYPES)]
        if spaced_type not in names:
            raise exceptions.CreateValueException(f"spaced_type must be one of the {names}")
        self._spaced_type = spaced_type
