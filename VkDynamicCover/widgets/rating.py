import datetime
import typing
from functools import reduce

from VkDynamicCover.widgets.profile import Profile
from apscheduler.schedulers.background import BackgroundScheduler
from vk_api.bot_longpoll import VkBotEventType
from loguru import logger

from .text import FormattingText
from .widget import Widget
from ..helpers.text_formatting.text_formatter import TextFormatter, FormatterFunction


class Rating(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.places: typing.List[RatingPlace] = kwargs.get("places")
        self.rating_info = kwargs.get("rating_info")

    def draw(self, surface):
        self.update_rating()

        surface = reduce(lambda x, y: y.draw(x), self.places, surface)

        if self.period_info:
            surface = self.period_info.draw(surface)

        return surface


class RatingPlace(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.profile = kwargs.get("profile")
        self.text = kwargs.get("text")

    def draw(self, surface):
        surface = self.profile.draw(surface)
        surface = self.text.draw(surface)
        return surface

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if text and not isinstance(text, RatingPlaceInfo):
            raise ValueError
        self._text = text

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, profile):
        if profile and not isinstance(profile, Profile):
            raise ValueError
        self._profile = profile


class RatingPlaceInfo(FormattingText):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.formatter = TextFormatter(FormatterFunction(function=RatingPlaceInfo.get_place_info))

    @staticmethod
    def get_place_info(user_id) -> typing.Dict[str, str]:
        if not self.user_id:
            return ""
        user = vk.get_user(vk_session=self.vk_session, user_id=self.user_id)
        return text.format(first_name=user["first_name"],
                           last_name=user["last_name"],
                           likes=self.member_rating["likes"],
                           comments=self.member_rating["comments"],
                           reposts=self.member_rating["reposts"],
                           points=self.member_rating["points"],
                           posts=self.member_rating["posts"],
                           donates=self.member_rating["donates"])
