from loguru import logger
from typing import List

from VkDynamicCover.widgets import *
from VkDynamicCover import builders


class WidgetCreator:
    def __init__(self, main_config: dict, widget_list: List[dict]):
        self._main_config = main_config
        self._widget_list = widget_list

    def create_widgets(self) -> List[widget.Widget]:
        res_list = [self.create_widget(**widget_info) for widget_info in self._widget_list]

        return res_list

    def create_widget(self, **kwargs) -> widget.Widget:
        tp = kwargs.get("type")
        builder = None
        if tp == text.Text.__name__:
            builder = builders.TextBuilder()
        elif tp == picture.Picture.__name__:
            builder = builders.PictureBuilder()
        elif tp == date.Date.__name__:
            builder = builders.DateBuilder()
        elif tp == statistics.Statistics.__name__:
            builder = builders.StatisticsBuilder()
        elif tp == rating.Rating.__name__:
            builder = builders.RatingBuilder()
        elif tp == profile.Profile.__name__:
            builder = builders.ProfileBuilder()
        else:
            logger.warning(f"Неизвестный тип виджета - {tp}")

        res_kwargs = {}
        res_kwargs.update(self._main_config)
        res_kwargs.update(kwargs)
        res = builder.create(**res_kwargs)
        logger.debug(f"Create widget {res}")
        return res

