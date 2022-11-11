from loguru import logger
from typing import List
import uuid

from VkDynamicCover.widgets import *
from VkDynamicCover.utils.widgets import other


class WidgetCreator:
    def __init__(self, main_config: dict, widget_list: List[dict]):
        self._main_config = main_config
        self._widget_list = self.create_widgets(widget_list)

    def create_widgets(self, widget_list: List[dict]) -> List[widget.Widget]:
        kw_widget_info = {}
        for w in widget_list:
            if "name" not in w:
                w["name"] = uuid.uuid4().hex
            kw_widget_info[w["name"]] = w
        for i in range(len(widget_list)):
            widget_list[i] = self._rec_fill_info(kw_widget_info, widget_list[i])

        res_list = [self.create_widget(**widget_info) for widget_info in widget_list]

        return res_list

    def _rec_fill_info(self, kw_widget_info: dict, widget_kwargs: dict) -> dict:
        if "parent" not in widget_kwargs:
            return widget_kwargs
        parent_name = widget_kwargs["parent"]
        if parent_name in kw_widget_info:
            self._rec_fill_info(kw_widget_info, kw_widget_info[parent_name])
            widget_kwargs = {**kw_widget_info[parent_name], **widget_kwargs}
        else:
            logger.warning(f"Для виджета {widget_kwargs['name']} не найден виджет-родитель {parent_name}")
        return widget_kwargs

    def create_widget(self, **kwargs) -> widget.Widget:
        tp = kwargs.get("type")
        if tp == text.Text.__name__:
            wid = text.Text
        elif tp == text_set.Message.__name__:
            wid = text_set.Message
        elif tp == picture.Picture.__name__:
            wid = picture.Picture
        elif tp == date.Date.__name__:
            wid = date.Date
        elif tp == random_picture.RandomPicture.__name__:
            wid = random_picture.RandomPicture
        elif tp == statistics.Statistics.__name__:
            wid = statistics.Statistics
        elif tp == rating.Rating.__name__:
            wid = rating.Rating
        elif tp == other.PeriodInfo.__name__:
            wid = other.PeriodInfo
        elif tp == profile.Profile.__name__:
            wid = profile.Profile
        elif tp == other.Avatar.__name__:
            wid = other.Avatar
        else:
            logger.warning(f"Неизвестный тип виджета - {tp}")
            wid = widget.Widget

        res_kwargs = {}
        res_kwargs.update(self._main_config)
        res_kwargs.update(kwargs)
        res = wid(**res_kwargs)
        logger.debug(f"Create widget {res}")
        return res

