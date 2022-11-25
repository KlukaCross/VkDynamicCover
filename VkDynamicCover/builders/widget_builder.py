from abc import abstractmethod

from VkDynamicCover.widgets.widget import Widget

PROPERTIES = ["xy", "type", "name"]


class WidgetBuilder:
    @abstractmethod
    def create(self, **kwargs) -> Widget:
        raise NotImplementedError
