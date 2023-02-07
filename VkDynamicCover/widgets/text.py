from functools import reduce

from PIL.Image import Image

from VkDynamicCover.types.spaced_types import SPACED_TYPES
from VkDynamicCover.widgets.widget import WidgetControl, WidgetDrawer, WidgetDesigner, WidgetInfo
from VkDynamicCover.text_formatting import TextFormatter, FormatterFunction, TextCalculator
from VkDynamicCover.utils import DrawTools
from VkDynamicCover.types import LIMITED_ACTION, exceptions, Coordinates
import re
import typing

DEFAULT_FONT_SIZE = 40
DEFAULT_SPACING = 4
DEFAULT_COLOR = "black"
DEFAULT_STROKE_WIDTH = 0


class TextControl(WidgetControl):
    __TYPE__ = "Text"


class TextDrawer(WidgetDrawer):
    def draw(self, surface: Image, info: "TextInfo") -> Image:
        for coors, txt in info.result_text.items():
            DrawTools.draw_text(surface=surface, text=txt, font_name=info.font_name,
                                font_size=info.font_size,
                                fill=info.fill, xy=(coors.x, coors.y), anchor=info.anchor, spacing=info.spacing,
                                direction=info.direction, stroke_width=info.stroke_width,
                                stroke_fill=info.stroke_fill)
        return surface


class TextDesigner(WidgetDesigner):
    def design(self, info: "TextInfo"):
        info.result_text = {Coordinates(info.xy): info.text}


class MultipleTextDesigner(TextDesigner):
    def __init__(self, designers: typing.List["TextDesigner"]):
        self._designers = designers

    def design(self, info: "TextInfo"):
        super().design(info)
        for designer in self._designers:
            designer.design(info)


class TextInfo(WidgetInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text = kwargs.get("text")
        self.xy = kwargs.get("xy", [0, 0])
        self.font_name = kwargs.get("font_name")
        self.font_size = kwargs.get("font_size", DEFAULT_FONT_SIZE)
        self.fill = kwargs.get("fill", DEFAULT_COLOR)
        self.anchor = kwargs.get("anchor")
        self.spacing = kwargs.get("spacing", DEFAULT_SPACING)
        self.direction = kwargs.get("direction")
        self.stroke_width = kwargs.get("stroke_width", DEFAULT_STROKE_WIDTH)
        self.stroke_fill = kwargs.get("stroke_fill")

        self.result_text: typing.Dict[Coordinates: str] = {}

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str):
        if text and not isinstance(text, str):
            raise exceptions.CreateTypeException("text", str, type(text))
        self._text = text if text else ""

    @property
    def font_name(self) -> str:
        return self._font_name

    @font_name.setter
    def font_name(self, font_name: str):
        if font_name and not isinstance(font_name, str):
            raise exceptions.CreateTypeException("font_name", str, type(font_name))
        self._font_name = font_name

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, font_size: int):
        if font_size and not isinstance(font_size, int):
            raise exceptions.CreateTypeException("font_size", int, type(font_size))
        self._font_size = font_size

    @property
    def fill(self) -> str:
        return self._fill

    @fill.setter
    def fill(self, fill: str):
        if fill and not isinstance(fill, str):
            raise exceptions.CreateTypeException("fill", str, type(fill))
        self._fill = fill

    @property
    def anchor(self) -> str:
        return self._anchor

    @anchor.setter
    def anchor(self, anchor: str):
        if anchor and not isinstance(anchor, str):
            raise exceptions.CreateTypeException("anchor", str, type(anchor))
        self._anchor = anchor

    @property
    def spacing(self) -> int:
        return self._spacing

    @spacing.setter
    def spacing(self, spacing: int):
        if spacing and not isinstance(spacing, int):
            raise exceptions.CreateTypeException("spacing", int, type(spacing))
        self._spacing = spacing

    @property
    def direction(self) -> str:
        return self._direction

    @direction.setter
    def direction(self, direction: str):
        if direction and not isinstance(direction, str):
            raise exceptions.CreateTypeException("direction", str, type(direction))
        self._direction = direction

    @property
    def stroke_width(self) -> int:
        return self._stroke_width

    @stroke_width.setter
    def stroke_width(self, stroke_width: int):
        if stroke_width and not isinstance(stroke_width, int):
            raise exceptions.CreateTypeException("stroke_width", int, type(stroke_width))
        self._stroke_width = stroke_width

    @property
    def stroke_fill(self) -> str:
        return self._stroke_fill

    @stroke_fill.setter
    def stroke_fill(self, stroke_fill: str):
        if stroke_fill and not isinstance(stroke_fill, str):
            raise exceptions.CreateTypeException("stroke_fill", str, type(stroke_fill))
        self._stroke_fill = stroke_fill

    @property
    def xy(self) -> Coordinates:
        return self._xy

    @xy.setter
    def xy(self, xy: typing.List[int]):
        if not isinstance(xy, list):
            raise exceptions.CreateTypeException("xy", list, type(xy))
        if len(xy) != 2:
            raise exceptions.CreateValueException("xy length", 2, len(xy))
        self._xy = Coordinates(xy)


class MultipleTextInfo(TextInfo):
    def __init__(self, infos: typing.List["WidgetInfo"], **kwargs):
        self.__dict__["_infos"] = infos
        super().__init__(**kwargs)

    def __getattr__(self, item):
        for info in self.__dict__["_infos"]:
            if hasattr(info, item):
                return getattr(info, item)
        raise AttributeError

    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
            return
        for info in self.__dict__["_infos"]:
            if hasattr(info, key):
                return setattr(info, key, value)
        super(WidgetInfo, self).__setattr__(key, value)


class FormattingTextDesigner(TextDesigner):
    def design(self, info: "FormattingTextInfo"):
        if not info.formatter:
            return
        for coors, txt in info.result_text.items():
            info.result_text[coors] = info.formatter.get_format_text(txt)


class FormattingTextInfo(TextInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._formatter = None

    @property
    def formatter(self) -> typing.Optional[TextFormatter]:
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: typing.Optional[TextFormatter]):
        if formatter and not isinstance(formatter, TextFormatter):
            raise exceptions.CreateTypeException("formatter", TextFormatter, type(formatter))
        self._formatter = formatter


class LimitedTextDesigner(TextDesigner):
    def design(self, info: "LimitedTextInfo"):
        for coors, txt in info.result_text.items():
            info.result_text[coors] = self._get_formatted_text(info, txt)

    @staticmethod
    def _get_formatted_text(info, text):
        limit_match = re.findall(r'\[.*]\[\d+]', text)
        for lim in limit_match:
            s = lim[1:lim.index(']')]
            max_len = int(lim[lim.rindex('[') + 1:-1])
            if info.limit_action == LIMITED_ACTION.DELETE.value:
                s = s[:max_len]
            elif info.limit_action == LIMITED_ACTION.NEWLINE.value:
                s = s[:max_len] + "\n"
            s += info.limit_end
            text = text.replace(lim, s)

        return text


class LimitedTextInfo(TextInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.limit_action = kwargs.get("limit_action")
        self.limit_end = kwargs.get("limit_end", "")

    @property
    def limit_action(self) -> str:
        return self._limit_action

    @limit_action.setter
    def limit_action(self, limit_action: str):
        if limit_action and not isinstance(limit_action, str):
            raise exceptions.CreateTypeException("limit_action", str, type(limit_action))
        names = [i.value for i in list(LIMITED_ACTION)]
        if limit_action not in names:
            raise exceptions.CreateValueException("limit_action", names, limit_action)
        self._limit_action = limit_action

    @property
    def limit_end(self) -> str:
        return self._limit_str

    @limit_end.setter
    def limit_end(self, limit_end: str):
        if limit_end and not isinstance(limit_end, str):
            raise exceptions.CreateTypeException("limit_end", str, type(limit_end))
        self._limit_str = limit_end


class SpacedTextDesigner(TextDesigner):
    def design(self, info: "SpacedTextInfo"):
        result = {}
        for coors, txt in info.result_text.items():
            result.update(self.spacing(txt, coors, info))
        info.result_text = result

    @staticmethod
    def spacing(text: str, coors: Coordinates, info: "SpacedTextInfo") -> typing.Dict[Coordinates, str]:
        result = {}

        def add():
            if from_ind == ind:
                return
            txt = text[from_ind:ind]
            if info.space_type == SPACED_TYPES.PRE_FORM.value and hasattr(info, "formatter"):
                txt = info.formatter.get_format_text(txt)

            result[Coordinates(shift_xy)] = txt

        def shift_x():
            res = int(re.search(r'\d+', h_match[h]).group(0))
            if info.space_type != SPACED_TYPES.WITH_START.value:
                res += \
                    DrawTools.get_text_size(re.sub(r'\{.*}', "", text[from_ind:ind]), info.font_name, info.font_size)[0]
            return res

        def shift_y():
            return int(re.search(r'\d+', v_match[v]).group(0))

        if not (info.space_type == SPACED_TYPES.PRE_FORM.value or not hasattr(info, "formatter")):
            text = info.formatter.get_format_text(text)

        v_match = re.findall(r':vspace\(\d+\):', text)
        h_match = re.findall(r':hspace\(\d+\):', text)
        shift_xy = [coors.x, coors.y]
        ind = -1
        from_ind = 0
        v = h = 0
        while v < len(v_match) and h < len(h_match):
            v_ind = text.find(v_match[v], ind + 1)
            h_ind = text.find(h_match[h], ind + 1)
            ind = min(v_ind, h_ind)

            add()

            if ind == v_ind:
                shift_xy[1] += shift_y()
                from_ind = ind + len(v_match[v])
                v += 1
            else:
                shift_xy[0] += shift_x()
                from_ind = ind + len(h_match[h])
                h += 1

        while v < len(v_match):
            v_ind = text.find(v_match[v], ind + 1)
            ind = v_ind
            add()
            shift_xy[1] += shift_y()
            from_ind = ind + len(v_match[v])
            v += 1

        while h < len(h_match):
            h_ind = text.find(h_match[h], ind + 1)
            ind = h_ind
            add()
            shift_xy[0] += shift_x()
            from_ind = ind + len(h_match[h])
            h += 1

        ind = len(text)
        add()

        return result


class SpacedTextInfo(TextInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.space_type = kwargs.get("space_type")

    @property
    def space_type(self) -> str:
        return self._spaced_type

    @space_type.setter
    def space_type(self, spaced_type: str):
        if spaced_type and not isinstance(spaced_type, str):
            raise exceptions.CreateTypeException("space_type", str, type(spaced_type))
        names = [i.value for i in list(SPACED_TYPES)]
        if spaced_type not in names:
            raise exceptions.CreateValueException("space_type", names, spaced_type)
        self._spaced_type = spaced_type


class CalcTextDesigner(TextDesigner):
    def design(self, info: "TextInfo"):
        for coors, txt in info.result_text.items():
            info.result_text[coors] = self._text_calc(txt)

    @staticmethod
    def _text_calc(text: str) -> str:
        calcs = re.findall(r'<.*>', text)
        for c in calcs:
            calc_txt = TextCalculator.text_calc(c[1:-1])
            text = text.replace(c, calc_txt, 1)
        return text
