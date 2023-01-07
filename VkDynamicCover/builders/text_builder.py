import typing
import re

from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.widgets.text import Text, LimitedText, SpacedText, FormattingText
from loguru import logger

PROPERTIES = ("text", "font_name", "font_size", "fill", "anchor", "spacing", "direction", "stroke_width", "stroke_fill", "limit", "limit_action", "limit_str")

_LIMIT_PROPERTIES = ("limit", "limit_action", "limit_str")


class TextBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Text:
        if not self._is_formatting_text(**kwargs) and not self._is_spaced_text(**kwargs) \
                and not self._is_limited_text(**kwargs):
            widget = Text
        elif self._is_spaced_text(**kwargs) and self._is_limited_text(**kwargs):
            logger.warning("Collision of spaced text and limited text")
            widget = Text
        elif self._is_spaced_text(**kwargs):
            widget = SpacedText
        elif self._is_limited_text(**kwargs):
            widget = LimitedText
        else:
            widget = FormattingText
        return widget(**kwargs)

    def _is_formatting_text(self, **kwargs) -> bool:
        return re.search(r'\{.*}', kwargs.get("text", "")) is not None

    def _is_spaced_text(self, **kwargs) -> bool:
        return kwargs.get("space_type") is not None #re.search(r'\[.space\(\d+\)]', kwargs.get("text", "")) is not None

    def _is_limited_text(self, **kwargs) -> bool:
        return "limit" in kwargs


