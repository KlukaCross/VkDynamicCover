from loguru import logger

from .message import Message
from ..utils import vk_tools


SUPPORTED_INFO_STATS = ["members_count"]

SUPPORTED_ACTIVITY_STATS = ["comments", "copies", "hidden", "likes", "subscribed", "unsubscribed"]

SUPPORTED_VISITORS_STATS = ["views", "visitors"]

SUPPORTED_REACH_STATS = ["reach", "reach_subscribers", "mobile_reach"]


class Statistics(Message):
    def __init__(self):
        super().__init__()
        self.interval = "day"

    def get_format_text(self, text):
        info_res = vk.get_group_info(vk_session=self.vk_session,
                                     group_id=self.group_id,
                                     fields=",".join(SUPPORTED_INFO_STATS))
        stat_res = vk.get_group_statistics(vk_session=self.vk_session, group_id=self.group_id, app_id=self.app_id,
                                           interval=self.interval)[0]

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

        return text.format(**stats)


    @property
    def interval(self) -> str:
        return self._interval

    @interval.setter
    def interval(self, interval: str):
        self._interval = interval
