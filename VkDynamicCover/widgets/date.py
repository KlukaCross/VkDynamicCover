import datetime
import math

from .text import Text

MONTHS_RUS = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль",
              "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

MONTHS_RUS_R = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
                "августа", "сентября", "октября", "ноября", "декабря"]

WEEKS_RUS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


class Date(Text):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.format = kwargs.get("format", "{day} {month_rus} {year}")

        self.shift = kwargs.get("shift", {})
        self.shift.setdefault("year", 0)
        self.shift.setdefault("month", 0)
        self.shift.setdefault("week", 0)
        self.shift.setdefault("day", 0)
        self.shift.setdefault("hour", 0)
        self.shift.setdefault("minute", 0)
        self.shift.setdefault("second", 0)

    def get_text(self) -> str:
        t = datetime.datetime.now() + datetime.timedelta(weeks=self.shift["week"],
                                                         days=self.shift["day"],
                                                         hours=self.shift["hour"],
                                                         minutes=self.shift["minute"],
                                                         seconds=self.shift["second"])

        t = t.replace(year=t.year + self.shift["year"] + math.trunc((t.month + self.shift["month"]) / 12),
                      month=(t.month + self.shift["month"]) % 12)

        self.set_specification()

        return self.format.format(year=t.year,
                                  month=t.month,
                                  month_rus=MONTHS_RUS[t.month-1],
                                  month_rus_r=MONTHS_RUS_R[t.month-1],
                                  week=t.isoweekday(),
                                  week_rus=WEEKS_RUS[t.weekday()],
                                  day=t.day,
                                  hour=t.hour,
                                  minute=t.minute,
                                  second=t.second)

    def set_specification(self):
        self.format = self.format\
            .replace("{month}", "{month:0>2}")\
            .replace("{day}", "{day:0>2}")\
            .replace("{hour}", "{hour:0>2}")\
            .replace("{minute}", "{minute:0>2}")\
            .replace("{second}", "{second:0>2}")
