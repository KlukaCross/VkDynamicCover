from loguru import logger

from VkDynamicCover.widgets import *
from VkDynamicCover.utils.widgets import other


def create_widget(config, **kwargs):
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
    elif name == "PeriodInfo":
        wid = other.PeriodInfo
    elif name == "Profile":
        wid = profile.Profile
    elif name == "Avatar":
        wid = other.Avatar
    else:
        logger.warning(f"Неизвестное имя виджета - {name}")
        wid = widget.Widget

    return wid(config, **kwargs)
