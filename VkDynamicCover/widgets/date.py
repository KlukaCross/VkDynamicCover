import datetime

import typing

from .text import FormattingText
from .widget import Widget
from VkDynamicCover.utils import TimeTools
from VkDynamicCover.types import exceptions
from ..helpers.text_formatting import FormatterFunction, TextInserter


class Date(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.shift = kwargs.get("shift", {})
        self.shift.setdefault("year", 0)
        self.shift.setdefault("month", 0)
        self.shift.setdefault("week", 0)
        self.shift.setdefault("day", 0)
        self.shift.setdefault("hour", 0)
        self.shift.setdefault("minute", 0)
        self.shift.setdefault("second", 0)

        self.text = kwargs.get("text")

    def draw(self, surface):
        return self.text.draw(surface)

    @staticmethod
    def get_format_text(shift) -> typing.Dict[str, str]:
        t = datetime.datetime.now()
        t = TimeTools.shift_time(t, shift)
        return TimeTools.format_time(t)

    @property
    def text(self) -> FormattingText:
        return self._text

    @text.setter
    def text(self, text: FormattingText):
        if text and not isinstance(text, FormattingText):
            raise exceptions.CreateTypeException(f"text must be FormattingText, not {type(text)}")
        self._text = text
        if self._text:
            self._text.formatter = TextInserter(FormatterFunction(self.get_format_text, shift=self.shift))

    @property
    def shift(self) -> dict:
        return self._shift

    @shift.setter
    def shift(self, shift: dict):
        if shift and not isinstance(shift, dict):
            raise exceptions.CreateTypeException(f"shift must be dict, not {type(shift)}")
        self._shift = shift

