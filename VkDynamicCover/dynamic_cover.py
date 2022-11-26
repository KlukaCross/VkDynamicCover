import time

from functools import reduce

from loguru import logger

from .utils import VkTools, DrawTools, widgets

COVER_WIDTH = 1590
COVER_HEIGHT = 530

SLEEP_SECONDS = 60


class DynamicCover:
    @logger.catch(reraise=True)
    def __init__(self, main_config: dict, widget_config: dict):

        token = main_config["token"]
        self.vk_session = VkTools.create_session(token)
        VkTools.init(self.vk_session, main_config["app_id"])
        self.group_id = main_config["group_id"]
        self.surface = DrawTools.create_surface(COVER_WIDTH, COVER_HEIGHT)

        show = widget_config["show"]
        show_cycle = show if isinstance(show, list) else [show]
        widget_list = widgets.WidgetCreator(main_config, widget_config["widgets"]).create_widgets()
        self.widget_drawing = widgets.CoverDrawing(surface=self.surface,
                                                   widget_list=widget_list,
                                                   show_cycle_names=show_cycle)

        sleep = main_config.get("sleep", SLEEP_SECONDS)
        self.sleep_cycle = [sleep] if isinstance(sleep, int) else sleep
        self.cur_sleep = 0

    def start(self):
        while True:
            self.update()
            time.sleep(self.sleep_cycle[self.cur_sleep])
            self.cur_sleep = (self.cur_sleep+1) % len(self.sleep_cycle)

    @logger.catch(reraise=False)
    def update(self):

        self.widget_drawing.draw()

        VkTools.push_cover(vk_session=self.vk_session, surface_bytes=DrawTools.get_byte_image(self.surface),
                      surface_width=self.surface.width, surface_height=self.surface.height,
                      group_id=self.group_id)
        logger.info(f"Обложка успешно обновлена")


class CoverDrawing:
    def __init__(self, surface, widget_list, show_cycle_names):
        self._surface = surface
        self._widget_list = widget_list
        self.show_cycle = []
        self._create_show_cycle(show_cycle_names=show_cycle_names)

        self.cur_show = 0

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

    def draw(self):
        reduce(lambda w: w.draw(self._surface), self.show_cycle[self.cur_show])
        self.cur_show = (self.cur_show+1) % len(self.show_cycle)
