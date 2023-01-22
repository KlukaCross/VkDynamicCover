import datetime

import typing

from .text import FormattingText
from .widget import Widget
from VkDynamicCover.utils import TimeTools
from VkDynamicCover.types import exceptions
from VkDynamicCover.text_formatting import FormatterFunction, TextInserter


class Date(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.shift = kwargs.get("shift", {})
        TimeTools.set_default_shift(self.shift)

        self.text = kwargs.get("text")

    def draw(self, surface):
        return self.text.draw(surface)

    @property
    def text(self) -> FormattingText:
        return self._text

    @text.setter
    def text(self, text: FormattingText):
        if text and not isinstance(text, FormattingText):
            raise exceptions.CreateTypeException("text", FormattingText, type(text))
        self._text = text
        if self._text:
            self._text.formatter = TextInserter(FormatterFunction(TimeTools.get_shift_and_format_time, shift=self.shift))

    @property
    def shift(self) -> dict:
        return self._shift

    @shift.setter
    def shift(self, shift: dict):
        if shift and not isinstance(shift, dict):
            raise exceptions.CreateTypeException(f"shift", dict, type(shift))
        self._shift = shift

