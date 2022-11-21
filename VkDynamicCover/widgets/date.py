import datetime

from .message import Message
from ..utils import time


class Date(Message):
    def __init__(self):
        super().__init__()

        self._shift = {}
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
    def shift(self) -> dict:
        return self._shift

