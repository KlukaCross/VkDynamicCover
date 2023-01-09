from abc import ABC, abstractmethod
from .subscriber import Subscriber
import typing


class Listener(ABC):
    def __init__(self):
        self._subscribers: typing.List[Subscriber] = []

    @abstractmethod
    def listen(self):
        pass

    def subscribe(self, sub: Subscriber):
        if sub not in self._subscribers:
            self._subscribers.append(sub)

    def update_all(self, event):
        for sub in self._subscribers:
            sub.update(event)
