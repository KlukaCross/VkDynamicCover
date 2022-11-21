import typing

from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.builders.text_builder import TextBuilder
from VkDynamicCover.widgets.message import Message

PROPERTIES = ("text",)


class MessageBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Message:
        widget = Message()
        self.wrap(widget, **kwargs)
        return widget

    def wrap(self, widget: Message, **properties):
        super().wrap(widget, **properties)
        text = properties.get("text", [])
        properties.pop("text")
        if isinstance(text, str) or isinstance(text, dict):
            text = [text]
        if not isinstance(text, list):
            raise ValueError
        for t in text:
            if isinstance(t, str):
                text_prop = {"text": t}
            elif isinstance(t, dict):
                text_prop = t
            else:
                raise ValueError
            text_prop.update(properties)
            widget.add_text(TextBuilder().create(**text_prop))
        text_prop = {"text": text}
        text_prop.update(properties)
        widget.add_text(TextBuilder().create(**text_prop))


