from abc import abstractmethod

from VkDynamicCover.widgets.widget import Widget


class WidgetBuilder:
    @abstractmethod
    def create(self, **kwargs) -> Widget or None:
        raise NotImplementedError
