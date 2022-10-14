import time

from loguru import logger

from .utils import vk, draw, widgets

COVER_WIDTH = 1590
COVER_HEIGHT = 530

SLEEP_SECONDS = 60


class DynamicCover:
    @logger.catch(reraise=True)
    def __init__(self, main_config: dict, widget_config: dict):

        token = main_config["token"]
        self.vk_session = vk.create_session(token)
        self.group_id = main_config["group_id"]
        self.surface = draw.create_surface(COVER_WIDTH, COVER_HEIGHT)

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

        vk.push_cover(vk_session=self.vk_session, surface_bytes=draw.get_byte_image(self.surface),
                      surface_width=self.surface.width, surface_height=self.surface.height,
                      group_id=self.group_id)
        logger.info(f"Обложка успешно обновлена")
