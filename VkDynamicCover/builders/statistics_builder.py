from VkDynamicCover.builders.text_builder import TextBuilder
from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.widgets.statistics import StatisticsControl, StatisticsDrawer, StatisticsDesigner, StatisticsInfo


class StatisticsBuilder(WidgetBuilder):
    def create(self, **kwargs) -> StatisticsControl:
        kwargs["text"] = TextBuilder().create(**kwargs)
        drawer = StatisticsDrawer()
        designer = StatisticsDesigner()
        info = StatisticsInfo(**kwargs)
        return StatisticsControl(drawer=drawer, designer=designer, info=info)
