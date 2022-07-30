from . import text, picture, date, random_picture, statistics, subscriber
from .widget import Widget

from loguru import logger


def get_widget(config: dict, **kwargs) -> widget.Widget:
    name = kwargs.get("name")

    if name == "text":
        wid = text.Text
    elif name == "picture":
        wid = picture.Picture
    elif name == "date":
        wid = date.Date
    elif name == "random_picture":
        wid = random_picture.RandomPicture
    elif name == "statistics":
        wid = statistics.Statistics
    elif name == "subscriber":
        wid = subscriber.Subscriber
    else:
        logger.warning(f"Неизвестное имя виджета - {name}")
        wid = Widget
    kwargs["config"] = config
    return wid(**kwargs)
