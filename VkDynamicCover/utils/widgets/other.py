import datetime

from VkDynamicCover.widgets.message import Message
from VkDynamicCover.widgets.picture import Picture

from VkDynamicCover.utils import vk_tools, draw, time, widgets
from VkDynamicCover.widgets.random_picture import RandomPicture


class PeriodInfo(Message):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        self.text_from = kwargs.get("date_from", "{day_z}.{month_z}.{year}")
        self.text_to = kwargs.get("date_to", "{day_z}.{month_z}.{year}")

        self.shift = kwargs.get("shift", {})
        self.shift.setdefault("year", 0)
        self.shift.setdefault("month", 0)
        self.shift.setdefault("week", 0)
        self.shift.setdefault("day", 0)
        self.shift.setdefault("hour", 0)
        self.shift.setdefault("minute", 0)
        self.shift.setdefault("second", 0)

        self.time_from = self.time_to = datetime.datetime.now()

    def get_format_text(self, text) -> str:
        return text.format(date_from=time.format_time(self.time_from, self.text_from),
                           date_to=time.format_time(self.time_to, self.text_to))

    def set_period(self, time_from: datetime.datetime, time_to: datetime.datetime):
        self.time_from = time.shift_time(time_from, self.shift)
        self.time_to = time.shift_time(time_to, self.shift)





