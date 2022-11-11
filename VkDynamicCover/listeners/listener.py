from abc import ABC, abstractmethod
from subcriber import Subscriber
import typing


class Listener(ABC):
    def __init__(self):
        self._subscribers: typing.List[Subscriber] = []

    @abstractmethod
    def listen(self):
        pass

    def subscribe(self, sub: Subscriber):
        self._subscribers.append(sub)

    def update_all(self, event):
        for sub in self._subscribers:
            sub.update(event)
