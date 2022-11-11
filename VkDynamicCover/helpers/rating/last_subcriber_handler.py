import typing
from VkDynamicCover.types import MetaSingleton
from VkDynamicCover.listeners import LongpollListener


class LastSubscriberHandler(metaclass=MetaSingleton, LongpollListener):
    def __init__(self):
        super().__init__()
        self._last_subscriber_ids: typing.List[int] = []
        self._max_subs: int = 0

    def update(self, event):
        pass

    def get_last_subscriber_ids(self, number: int) -> typing.List[int]:
        return self._last_subscriber_ids[:number]

    def add_track_last_subscribers(self, max_subs: int):
        self._max_subs = max(self._max_subs, max_subs)
