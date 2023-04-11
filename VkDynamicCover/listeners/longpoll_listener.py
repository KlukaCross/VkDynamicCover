import requests
from VkDynamicCover.plugins.scheduler import Scheduler
from loguru import logger

from VkDynamicCover.utils import VkTools
from .listener import Listener
from VkDynamicCover.types import MetaSingleton


class LongpollListener(Listener, metaclass=MetaSingleton):
    def __init__(self, group_id: int):
        if hasattr(self, "group_id"):
            return
        super().__init__()
        self.group_id = group_id
        Scheduler.add_job(self.listen)

    def listen(self):
        longpoll = VkTools.get_longpoll(group_id=self.group_id)
        while Scheduler.running:
            events = VkTools.check_longpoll(longpoll)
            if not events:
                continue
            for event in events:
                self.update_all(event)
