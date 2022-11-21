from abc import abstractmethod

from VkDynamicCover.widgets.widget import Widget

PROPERTIES = ["xy", "type", "name"]


class WidgetBuilder:
    @abstractmethod
    def create(self, **kwargs) -> Widget:
        raise NotImplementedError

    def wrap(self, widget: Widget, **properties):
        widget.xy = properties.get("xy")
        widget.type = properties.get("type")
        widget.name = properties.get("name")
