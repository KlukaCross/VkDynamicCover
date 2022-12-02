import time

from functools import reduce

from PIL.Image import Image
from loguru import logger

from .types import exceptions
from .utils import VkTools, DrawTools, WidgetCreator

COVER_WIDTH = 1920
COVER_HEIGHT = 768

SLEEP_SECONDS = 60

VERSION_MAIN_CONFIG = "0.1"
VERSION_COVER_CONFIG = "0.1"


class DynamicCover:
    @logger.catch(reraise=True)
    def __init__(self, main_config: dict, cover_config: dict):

        if main_config.get("VERSION") != VERSION_MAIN_CONFIG:
            raise exceptions.CreateInvalidVersion("main_config")

        if cover_config.get("VERSION") != VERSION_COVER_CONFIG:
            raise exceptions.CreateInvalidVersion("widgets_config")

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

        sleep = main_config.get("sleep", SLEEP_SECONDS)
        self.sleep_cycle = [sleep] if isinstance(sleep, int) else sleep
        self.cur_sleep = 0

    def start(self):
        while True:
            self.cover_drawing.update()
            time.sleep(self.sleep_cycle[self.cur_sleep])
            self.cur_sleep = (self.cur_sleep + 1) % len(self.sleep_cycle)


class CoverDrawing:
    def __init__(self, widget_list, show_cycle_names, group_id):
        self._widget_list = widget_list
        self.show_cycle = []
        self._create_show_cycle(show_cycle_names=show_cycle_names)
        self._surface = DrawTools.create_surface(COVER_WIDTH, COVER_HEIGHT)
        self._group_id = group_id

        self.cur_show = 0

    @logger.catch(reraise=False)
    def update(self):
        self._surface = self.draw(self._surface)

        VkTools.push_cover(surface_bytes=DrawTools.get_byte_image(self._surface),
                           surface_width=self._surface.width, surface_height=self._surface.height,
                           group_id=self._group_id)
        logger.info(f"Обложка успешно обновлена")

    def draw(self, surface: Image) -> Image:
        DrawTools.clear(surface)
        surface = reduce(lambda s, w: w.draw(s), self.show_cycle[self.cur_show], surface)
        self.cur_show = (self.cur_show + 1) % len(self.show_cycle)
        return surface

    def _create_show_cycle(self, show_cycle_names):
        def get_widget(name: str):
            for wid in self._widget_list:
                if name == wid.name:
                    return wid
            logger.warning(f"Not found widget with name {name}")

        for w in show_cycle_names:
            if not isinstance(w, list):
                widget = get_widget(w)
                if widget:
                    self.show_cycle.append([widget])
                continue

            tmp_lst = []
            for ww in w:
                widget = get_widget(ww)
                if widget:
                    tmp_lst.append(widget)
            self.show_cycle.append(tmp_lst)

