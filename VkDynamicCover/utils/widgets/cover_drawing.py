from typing import Union, List
from functools import reduce

from loguru import logger


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
