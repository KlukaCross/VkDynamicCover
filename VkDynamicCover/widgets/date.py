import datetime

import typing

from PIL.Image import Image

from .text import TextControl
from .widget import WidgetControl, WidgetInfo, WidgetDrawer
from VkDynamicCover.utils import TimeTools
from VkDynamicCover.types import exceptions
from VkDynamicCover.text_formatting import FormatterFunction, TextInserter


class DateControl(WidgetControl):
    __TYPE__ = "Date"


class DateDrawer(WidgetDrawer):
    def draw(self, surface: Image, info: "DateInfo") -> Image:
        return info.text.draw(surface)


class DateInfo(WidgetInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.shift = kwargs.get("shift", {})
        TimeTools.set_default_shift(self.shift)

        self.text = kwargs.get("text")

    @property
    def text(self) -> TextControl:
        return self._text

    @text.setter
    def text(self, text: TextControl):
        if text and not isinstance(text, TextControl):
            raise exceptions.CreateTypeException("text", TextControl, type(text))
        self._text = text
        if self._text:
            self._text.formatter = TextInserter(
                FormatterFunction(TimeTools.get_shift_and_format_time, shift=self.shift))

    @property
    def shift(self) -> dict:
        return self._shift

    @shift.setter
    def shift(self, shift: dict):
        if shift and not isinstance(shift, dict):
            raise exceptions.CreateTypeException(f"shift", dict, type(shift))
        self._shift = shift
