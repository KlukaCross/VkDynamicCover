from loguru import logger

from .text import Text
from ..utils import vk


class Statistics(Text):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.format = kwargs.get("format", "")
        self.interval = kwargs.get("interval", "day")

    def get_text(self) -> str:
        group_id = self.config.get("group_id")
        app_id = self.config.get("app_id")
        if not app_id:
            logger.error("В файле config отсутствует параметр app_id")
            return ""
        info_res = vk.get_group_info(vk_session=self.vk_session, group_id=group_id, fields="members_count")
        stat_res = vk.get_group_statistics(vk_session=self.vk_session, group_id=group_id, app_id=app_id,
                                           interval=self.interval)[0]
        interval_stats = {**stat_res.get("activity", {}), **stat_res.get("visitors", {}), **stat_res.get("reach", {})}
        text = self.format.format(members_count=info_res["members_count"],
                                  comments=interval_stats.get("comments", 0),
                                  copies=interval_stats.get("copies", 0),
                                  hidden=interval_stats.get("hidden", 0),
                                  likes=interval_stats.get("likes", 0),
                                  subscribed=interval_stats.get("subscribed", 0),
                                  unsubscribed=interval_stats.get("unsubscribed", 0),
                                  views=interval_stats.get("views", 0),
                                  visitors=interval_stats.get("visitors", 0),
                                  reach=interval_stats.get("reach", 0),
                                  reach_subscribers=interval_stats.get("reach_subscribers", 0),
                                  mobile_reach=interval_stats.get("mobile_reach", 0))
        return text
