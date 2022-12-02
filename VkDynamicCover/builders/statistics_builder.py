from VkDynamicCover.builders.text_builder import TextBuilder
from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.widgets.statistics import Statistics

PROPERTIES = ("interval", "group_id")


class StatisticsBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Statistics:
        kwargs["text"] = TextBuilder().create(**kwargs)
        widget = Statistics(**kwargs)
        return widget
