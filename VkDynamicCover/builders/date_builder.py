from VkDynamicCover.builders.text_builder import TextBuilder
from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.widgets.date import Date


class DateBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Date:
        kwargs["text"] = TextBuilder().create(**kwargs)
        return Date(**kwargs)
