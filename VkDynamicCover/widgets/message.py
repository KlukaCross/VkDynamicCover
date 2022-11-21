import typing
from functools import reduce

from VkDynamicCover.widgets.text import Text
from VkDynamicCover.widgets.widget import Widget


class Message(Widget):
    def __init__(self):
        super().__init__()

        self._text_widgets: typing.List[Text] = []

        self.formatter = None

    def draw(self, surface):
        surface = super().draw(surface)
        surface = reduce(lambda x, y: y.draw(x), self._text_widgets, surface)
        return surface

    def add_text(self, text: Text):
        text.formatter = self.formatter
        self._text_widgets.append(text)

