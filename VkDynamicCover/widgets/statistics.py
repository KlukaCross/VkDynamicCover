from loguru import logger

from .text import Text
from ..utils import vk


class Statistics(Text):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.format = kwargs.get("format", **kwargs)
        self.interval = kwargs.get("interval", "day")

    def get_text(self) -> str:
        group_id = self.config.get("group_id")
        app_id = self.config.get("app_id")
        if not app_id:
            logger.error("В файле config отсутствует параметр app_id")
            return ""
        info_res = vk.get_group_info(vk_session=self.vk_session, group_id=group_id, fields="members_count")
        stat_res = vk.get_group_statistics(vk_session=self.vk_session, group_id=group_id, app_id=app_id,
                                           interval=self.interval)
        text = self.format.format(members_count=info_res["members_count"],
                                  **stat_res["activity"], **stat_res["visitors"], **stat_res["reach"])
        return text
