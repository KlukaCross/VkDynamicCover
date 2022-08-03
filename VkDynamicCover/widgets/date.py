import datetime
import math

from .text_set import TextSet
from ..utils import time


class Date(TextSet):
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

    def get_format_text(self, text) -> str:
        t = datetime.datetime.now()
        t += datetime.timedelta(weeks=self.shift["week"],
                                   days=self.shift["day"],
                                   hours=self.shift["hour"],
                                   minutes=self.shift["minute"],
                                   seconds=self.shift["second"])

        t = t.replace(year=t.year + self.shift["year"] + math.trunc((t.month + self.shift["month"]) / 12),
                            month=(t.month + self.shift["month"]) % 12)
        return time.format_time(t, text)

