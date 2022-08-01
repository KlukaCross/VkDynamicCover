from loguru import logger

from .text_set import TextSet
from ..utils import vk


SUPPORTED_INFO_STATS = ["members_count"]

SUPPORTED_ACTIVITY_STATS = ["comments", "copies", "hidden", "likes", "subscribed", "unsubscribed"]

SUPPORTED_VISITORS_STATS = ["views", "visitors"]

SUPPORTED_REACH_STATS = ["reach", "reach_subscribers", "mobile_reach"]


class Statistics(TextSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interval = kwargs.get("interval", "day")
        self.group_id = kwargs.get("group_id") or self.config["group_id"]
        self.app_id = self.config.get("app_id")
        if not self.app_id:
            logger.error("В файле config отсутствует параметр app_id")

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
