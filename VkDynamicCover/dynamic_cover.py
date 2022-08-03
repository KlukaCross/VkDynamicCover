from functools import reduce

from loguru import logger

from .utils import vk, draw, widgets

COVER_WIDTH = 1590
COVER_HEIGHT = 530

BACKGROUND = "background"
FRONTGROUND = "frontground"


class DynamicCover:
    @logger.catch(reraise=True)
    def __init__(self, config: dict):

        token = config["token"]
        self.vk_session = vk.create_session(token)
        self.group_id = config["group_id"]
        self.surface = draw.create_surface(COVER_WIDTH, COVER_HEIGHT)

        self.widget_sets = self.get_widget_sets(
            widget_sets=config.get("widget_sets"),
            group_id=self.group_id,
            app_id=config.get("app_id"),
            vk_session=self.vk_session
        )

        self.widget_cycle = config.get("widget_cycle", [])
        self.cur_widget_set = 0 if len(self.widget_cycle) > 0 else -1

    @logger.catch(reraise=True)
    def update(self):
        self.surface = reduce(lambda surf, wid: wid.draw(surf), self.widget_sets.get(BACKGROUND, []), self.surface)

        if self.cur_widget_set >= 0:
            set_name = self.widget_cycle[self.cur_widget_set]
            self.surface = reduce(lambda surf, wid: wid.draw(surf), self.widget_sets.get(set_name, []), self.surface)

            if set_name not in self.widget_sets:
                logger.warning(f"Набор виджетов {set_name} не найден")

        self.surface = reduce(lambda surf, wid: wid.draw(surf), self.widget_sets.get(FRONTGROUND, []), self.surface)

        vk.push_cover(vk_session=self.vk_session, surface_bytes=draw.get_byte_image(self.surface),
                      surface_width=self.surface.width, surface_height=self.surface.height,
                      group_id=self.group_id)
        logger.info(f"Обложка успешно обновлена")

        if self.cur_widget_set < 0:
            return
        self.cur_widget_set = self.cur_widget_set + 1 if self.cur_widget_set < len(self.widget_cycle) - 1 else 0

    @logger.catch(reraise=True)
    def get_widget_sets(self, widget_sets, **config) -> dict:
        for key, value in widget_sets.items():
            if isinstance(value, dict):
                widget_sets[key] = [widgets.create_widget(**config, **value)]
            else:
                widget_sets[key] = [widgets.create_widget(**config, **wid) for wid in value]
        return widget_sets
