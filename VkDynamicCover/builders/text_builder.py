import typing

from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.widgets.text import Text, LimitedText

PROPERTIES = ("text", "font_name", "font_size", "fill", "anchor", "spacing", "direction", "stroke_width", "stroke_fill", "limit", "limit_action", "limit_str")

_LIMIT_PROPERTIES = ("limit", "limit_action", "limit_str")


class TextBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Text:
        widget = LimitedText() if set(_LIMIT_PROPERTIES).intersection(kwargs.keys()) else Text()
        self.wrap(widget)
        return widget

    def wrap(self, widget: typing.Union[Text, LimitedText], **properties):
        super().wrap(widget, **properties)
        if set(_LIMIT_PROPERTIES).intersection(properties.keys()):
            widget.max = properties.get("limit")
            widget.action = properties.get("limit_action")
            widget.end = properties.get("limit_str")

        widget.text = properties.get("text")
        widget.xy = properties.get("xy")
        widget.font_name = properties.get("font_name")
        widget.font_size = properties.get("font_size")
        widget.fill = properties.get("fill")
        widget.anchor = properties.get("anchor")
        widget.spacing = properties.get("spacing")
        widget.direction = properties.get("direction")
        widget.stroke_width = properties.get("stroke_width")
        widget.stroke_fill = properties.get("stroke_fill")
