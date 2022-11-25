import datetime

from .text import Text
from .widget import Widget
from ..utils import time


class Date(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get("text")

        self.shift = kwargs.get("shift")
        self.shift.setdefault("year", 0)
        self.shift.setdefault("month", 0)
        self.shift.setdefault("week", 0)
        self.shift.setdefault("day", 0)
        self.shift.setdefault("hour", 0)
        self.shift.setdefault("minute", 0)
        self.shift.setdefault("second", 0)

    def get_format_text(self, text) -> str:
        t = datetime.datetime.now()
        t = time.shift_time(t, self.shift)
        return time.format_time(t, text)

    @property
    def text(self) -> Text:
        return self._text

    @text.setter
    def text(self, text: Text):
        if text and not isinstance(text, Text):
            raise ValueError
        self._text = text

    @property
    def shift(self) -> dict:
        return self._shift

    @shift.setter
    def shift(self, shift: dict):
        if not shift:
            self.shift = {}
        self._shift = shift

