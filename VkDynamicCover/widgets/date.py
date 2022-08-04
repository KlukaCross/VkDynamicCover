import datetime

from .text_set import TextSet
from ..utils import time


class Date(TextSet):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        self.shift = kwargs.get("shift", {})
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


