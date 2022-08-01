from . import text, picture, date, random_picture, statistics, subscriber, text_set
from .widget import Widget

from loguru import logger


def get_widget(config: dict, **kwargs) -> widget.Widget:
    name = kwargs.get("name")

    if name == "Text":
        wid = text.Text
    elif name == "TextSet":
        wid = text_set.TextSet
    elif name == "Picture":
        wid = picture.Picture
    elif name == "Date":
        wid = date.Date
    elif name == "RandomPicture":
        wid = random_picture.RandomPicture
    elif name == "Statistics":
        wid = statistics.Statistics
    elif name == "Subscriber":
        wid = subscriber.Subscriber
    else:
        logger.warning(f"Неизвестное имя виджета - {name}")
        wid = Widget
    kwargs["config"] = config
    return wid(**kwargs)
