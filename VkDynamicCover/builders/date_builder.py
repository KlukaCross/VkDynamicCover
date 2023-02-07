from VkDynamicCover.builders.text_builder import TextBuilder
from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.widgets.date import DateControl, DateDrawer, DateInfo
from VkDynamicCover.widgets.widget import WidgetDesigner


class DateBuilder(WidgetBuilder):
    def create(self, **kwargs) -> DateControl:
        kwargs["text"] = TextBuilder().create(**kwargs)
        drawer = DateDrawer()
        designer = WidgetDesigner()
        info = DateInfo(**kwargs)
        return DateControl(drawer=drawer, designer=designer, info=info)
