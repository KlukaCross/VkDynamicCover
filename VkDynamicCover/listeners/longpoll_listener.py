from listener import Listener
from VkDynamicCover.types import MetaSingleton


class LongpollListener(metaclass=MetaSingleton, Listener):
    def listen(self):
        pass
