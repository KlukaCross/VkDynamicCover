import profile

from loguru import logger

from VkDynamicCover.widgets import *
from VkDynamicCover.utils.widgets import other


def create_widget(*args, **kwargs):
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

    if not args:
        return wid(**kwargs)

    if name == "Text":
        if isinstance(args[0], dict):
            kwargs.update(args[0].items())
        elif isinstance(args[0], str):
            kwargs["text"] = args[0]

    elif name in ["TextSet", "Date", "PeriodInfo", "Statistics", "Profile"]:
        if isinstance(args[0], dict):
            if "text" in args[0]:
                kwargs["texts"] = [args[0]]
            else:
                kwargs.update(args[0].items())
        else:
            kwargs["texts"] = args
    else:
        if args and isinstance(args[0], dict):
            kwargs.update(args[0].items())

    return wid(**kwargs)
