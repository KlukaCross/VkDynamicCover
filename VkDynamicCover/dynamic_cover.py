import time

from functools import reduce

import typing
from PIL.Image import Image
from loguru import logger

from VkDynamicCover.plugins.scheduler import Scheduler
from VkDynamicCover.types import exceptions
from VkDynamicCover.utils import VkTools, DrawTools
from VkDynamicCover.widgets.widget import WidgetControl
from VkDynamicCover.widgets import *
from VkDynamicCover import builders

COVER_WIDTH = 1920
COVER_HEIGHT = 768

DEFAULT_SLEEP_SECONDS = 60

VERSION_MAIN_CONFIG = 0.1
VERSION_COVER_CONFIG = 1.1


def check_version(user_version: str, actual_version: float, name_config: str):
    if int(float(user_version)) != int(actual_version):
        raise exceptions.CreateInvalidVersion(name_config)
    if float(user_version) != actual_version:
        logger.warning(f"Not actual version for {name_config}! Actual version is {actual_version}")


class DynamicCover:
    @logger.catch(onerror=lambda _: exit(1))
    def __init__(self, main_config: dict, cover_config: dict):

        check_version(main_config.get("VERSION"), VERSION_MAIN_CONFIG, "main_config")
        check_version(cover_config.get("VERSION"), VERSION_COVER_CONFIG, "cover_config")

        token = main_config["token"]
        self.vk_session = VkTools.create_session(token)
        VkTools.init(self.vk_session, main_config.get("app_id"))

        show = cover_config["show"]
        show_cycle = show if isinstance(show, list) else [show]
        widget_list = WidgetCreator(main_config, cover_config["widgets"]).create_widgets()
        group_id = main_config["group_id"]
        self.cover_drawing = CoverDrawing(widget_list=widget_list,
                                          show_cycle_names=show_cycle,
                                          group_id=group_id)

        sleep = main_config.get("sleep", DEFAULT_SLEEP_SECONDS)
        self.sleep_cycle = [sleep] if isinstance(sleep, int) else sleep
        self.cur_sleep = 0

    @logger.catch(onerror=lambda _: exit(1))
    def start(self):
        while Scheduler.running:
            self.cover_drawing.update()
            time.sleep(self.sleep_cycle[self.cur_sleep])
            self.cur_sleep = (self.cur_sleep + 1) % len(self.sleep_cycle)


class WidgetCreator:
    def __init__(self, main_config: dict, widget_list: typing.List[dict]):
        self._main_config = main_config
        self._widget_list = widget_list

    def create_widgets(self) -> typing.List[widget.WidgetControl]:
        res_list = []
        for widget_info in self._widget_list:
            w = self.create_widget(**widget_info)
            if w:
                res_list.append(w)

        return res_list

    def create_widget(self, **kwargs) -> widget.WidgetControl or None:
        tp = kwargs.get("type")
        if tp == text.TextControl.__TYPE__:
            builder = builders.TextBuilder()
        elif tp in [picture.PictureControl.__TYPE__, picture.VkAvatarControl.__TYPE__, picture.RandomPictureControl.__TYPE__]:
            builder = builders.PictureBuilder()
        elif tp == date.DateControl.__TYPE__:
            builder = builders.DateBuilder()
        elif tp == statistics.StatisticsControl.__TYPE__:
            builder = builders.StatisticsBuilder()
        elif tp == rating.RatingControl.__TYPE__:
            builder = builders.RatingBuilder()
        elif tp == profile.ProfileControl.__TYPE__:
            builder = builders.ProfileBuilder()
        else:
            logger.warning(f"Неизвестный тип виджета - {tp}")
            return

        res_kwargs = {}
        res_kwargs.update(self._main_config)
        res_kwargs.update(kwargs)
        res = builder.create(**res_kwargs)
        if not res:
            raise exceptions.CreateException(f"failed to create widget with params {res_kwargs}")
        logger.debug(f"Create widget {res}")
        return res


class CoverDrawing:
    def __init__(self, widget_list, show_cycle_names, group_id):
        self._widget_list: typing.List[WidgetControl] = widget_list
        self._show_cycle: typing.List[typing.List[WidgetControl]] = []
        self._create_show_cycle(show_cycle_names=show_cycle_names)
        self._surface = DrawTools.create_surface(COVER_WIDTH, COVER_HEIGHT)
        self._group_id = group_id

        self._cur_show = 0

    def update(self):
        self._surface = self.draw(self._surface)

        photo = DrawTools.get_bytesio_image(self._surface)

        VkTools.push_cover(surface_bytes=photo,
                           surface_width=self._surface.width,
                           surface_height=self._surface.height,
                           group_id=self._group_id)
        photo.close()
        logger.info(f"Обложка успешно обновлена")

    def draw(self, surface: Image) -> Image:
        DrawTools.clear(surface)
        surface = reduce(lambda s, w: w.draw(s), self._show_cycle[self._cur_show], surface)
        self._cur_show = (self._cur_show + 1) % len(self._show_cycle)
        return surface

    def _create_show_cycle(self, show_cycle_names):
        def get_widget(name: str):
            for wi in self._widget_list:
                if name == wi.info.name:
                    return wi
            logger.warning(f"Not found widget with name {name}")

        for w in show_cycle_names:
            if not isinstance(w, list):
                wid = get_widget(w)
                if wid:
                    self._show_cycle.append([wid])
                continue

            tmp_lst = []
            for ww in w:
                wid = get_widget(ww)
                if wid:
                    tmp_lst.append(wid)
            self._show_cycle.append(tmp_lst)

