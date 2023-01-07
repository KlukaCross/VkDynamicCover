import typing
from loguru import logger

from VkDynamicCover.helpers import text_formatting as formatting
from .text import FormattingText
from .widget import Widget
from VkDynamicCover.utils import VkTools
from VkDynamicCover.types import exceptions

SUPPORTED_INFO_STATS = ("members_count",)

SUPPORTED_ACTIVITY_STATS = ("comments", "copies", "hidden", "likes", "subscribed", "unsubscribed")

SUPPORTED_VISITORS_STATS = ("views", "visitors")

SUPPORTED_REACH_STATS = ("reach", "reach_subscribers", "mobile_reach")


class Statistics(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get("text")
        self.interval = kwargs.get("interval")
        self.group_id = kwargs.get("group_id")
        self.text.formatter = formatting.TextInserter(
            function=formatting.FormatterFunction(Statistics.get_full_info,
                                                  group_id=self.group_id,
                                                  interval=self.interval)
        )

    def draw(self, surface):
        return self.text.draw(surface)

    @staticmethod
    def get_full_info(group_id: int, interval: str) -> typing.Dict[str, str]:
        info_res = VkTools.get_group_info(group_id=group_id, fields=",".join(SUPPORTED_INFO_STATS))
        stat_res = VkTools.get_group_statistics(group_id=group_id, interval=interval)[0]

        interval_stats = {**stat_res.get("activity", {}),
                          **stat_res.get("visitors", {}),
                          **stat_res.get("reach", {}),
                          **info_res}

        stats = {x: interval_stats.get(x, 0) for x in [
            *SUPPORTED_INFO_STATS,
            *SUPPORTED_ACTIVITY_STATS,
            *SUPPORTED_VISITORS_STATS,
            *SUPPORTED_REACH_STATS
        ]}

        return stats

    @property
    def interval(self) -> str:
        return self._interval

    @interval.setter
    def interval(self, interval: str):
        if interval and not isinstance(interval, str):
            raise exceptions.CreateTypeException("interval", str, type(interval))
        self._interval = interval

    @property
    def text(self) -> FormattingText:
        return self._text

    @text.setter
    def text(self, text: FormattingText):
        if text and not isinstance(text, FormattingText):
            raise exceptions.CreateTypeException("text", FormattingText, type(text))
        self._text = text

    @property
    def group_id(self) -> int:
        return self._group_id

    @group_id.setter
    def group_id(self, group_id: int):
        if not isinstance(group_id, int):
            raise exceptions.CreateTypeException("group_id", int, type(group_id))
        self._group_id = group_id
