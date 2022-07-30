from loguru import logger

from .utils import vk, draw
from .widgets import get_widget

COVER_WIDTH = 1590
COVER_HEIGHT = 530


class DynamicCover:
    def __init__(self, config: dict):
        self.config = config

        self.vk_session = vk.create_session(self.config["token"])
        self.surface = draw.create_surface(COVER_WIDTH, COVER_HEIGHT)

        self.widget_sets = self.get_widget_sets()

        self.widget_program = self.config.get("widget_program", [])
        self.now_program = 0 if len(self.widget_program) > 0 else -1

    @logger.catch(reraise=True)
    def update(self):
        for w in self.widget_sets.get("background", []):
            self.surface = w.draw(self.surface)

        if self.now_program >= 0:
            set_name = self.widget_program[self.now_program]
            for w in self.widget_sets.get(set_name, []):
                self.surface = w.draw(self.surface)
            if set_name not in self.widget_sets:
                logger.warning(f"Набор виджетов {set_name} не найден")

        for w in self.widget_sets.get("frontground", []):
            self.surface = w.draw(self.surface)

        vk.push_cover(vk_session=self.vk_session, surface_bytes=draw.get_byte_image(self.surface),
                            surface_width=self.surface.width, surface_height=self.surface.height,
                            group_id=self.config["group_id"])
        logger.info(f"Обложка успешно обновлена")

        if self.now_program < 0:
            return
        self.now_program = self.now_program+1 if self.now_program < len(self.widget_program)-1 else 0

    @logger.catch(reraise=True)
    def get_widget_sets(self) -> dict:
        sets = self.config.get("widget_sets", {})
        for key, value in sets.items():
            if isinstance(value, dict):
                sets[key] = [get_widget(config=self.config, vk_session=self.vk_session, **value)]
            else:
                sets[key] = [get_widget(config=self.config, vk_session=self.vk_session, **wid) for wid in value]
        return sets
