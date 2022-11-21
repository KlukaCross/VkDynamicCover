from VkDynamicCover.builders.message_builder import MessageBuilder
from VkDynamicCover.widgets.statistics import Statistics

PROPERTIES = ("interval", "group_id")


class StatisticsBuilder(MessageBuilder):
    def create(self, **kwargs) -> Statistics:
        widget = Statistics()
        self.wrap(widget, **kwargs)
        return widget

    def wrap(self, widget: Statistics, **properties):
        super().wrap(widget, **properties)
        widget.interval = properties.get("interval")
        widget.group_id = properties.get("group_id")
