import requests
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from VkDynamicCover.utils import VkTools
from listener import Listener
from VkDynamicCover.types import MetaSingleton


class LongpollListener(metaclass=MetaSingleton, Listener):
    def __init__(self, group_id: int):
        super().__init__()
        self.group_id = group_id
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=self.listen,
            kwargs={
                "self": self
            }
        )
        self.scheduler.start()

    def listen(self):
        longpoll = VkTools.get_longpoll()
        while True:
            try:
                for event in longpoll.listen():
                    self.update_all(event)
            except requests.exceptions.ReadTimeout as e:
                logger.warning(f"Время ожидания ответа истекло.\n{e}")

