from abc import abstractmethod

from VkDynamicCover.widgets.widget import WidgetControl


class WidgetBuilder:
    @abstractmethod
    def create(self, **kwargs) -> WidgetControl or None:
        raise NotImplementedError
