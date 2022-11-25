import typing
from loguru import logger

from VkDynamicCover.helpers import text_formatting as formatting
from .text import Text
from .widget import Widget
from ..utils import vk_tools
from VkDynamicCover.utils import VkTools


SUPPORTED_INFO_STATS = ("members_count",)

SUPPORTED_ACTIVITY_STATS = ("comments", "copies", "hidden", "likes", "subscribed", "unsubscribed")

SUPPORTED_VISITORS_STATS = ("views", "visitors")

SUPPORTED_REACH_STATS = ("reach", "reach_subscribers", "mobile_reach")


class Statistics(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get("text")
        self.interval = kwargs.get("interval")
        self.formatter = formatting.TextInserter(
            function=formatting.FormatterFunction(Statistics.get_full_info,
                                                  group_id=self.group_id,
                                                  interval=self.interval)
        )

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
        self._interval = interval

    @property
    def text(self) -> Text:
        return self._text

    @text.setter
    def text(self, text: Text):
        if text and not isinstance(text, Text):
            raise ValueError
        self._text = text
