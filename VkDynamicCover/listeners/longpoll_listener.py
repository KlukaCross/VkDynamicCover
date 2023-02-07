import requests
from apscheduler.schedulers.background import BackgroundScheduler
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
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=self.listen,
        )
        self.scheduler.start()

    def listen(self):
        longpoll = VkTools.get_longpoll(group_id=self.group_id)
        while True:
            try:
                for event in longpoll.listen():
                    self.update_all(event)
            except requests.exceptions.ReadTimeout as e:
                logger.warning(f"Время ожидания ответа истекло.\n{e}")

