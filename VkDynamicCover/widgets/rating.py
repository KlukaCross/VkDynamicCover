import datetime
import typing
from functools import reduce

from VkDynamicCover.widgets.profile import Profile, UserInfo
from VkDynamicCover.widgets.picture import VkAvatar, RandomAlbumPicture

from .text import Text
from .widget import Widget
from VkDynamicCover.text_formatting import FormatterFunction
from VkDynamicCover.text_formatting import TextInserter
from VkDynamicCover.rating_handler.rating_info import RatingInfo
from VkDynamicCover.types import exceptions, MemberInfoTypes
from VkDynamicCover.utils import TimeTools

from loguru import logger


class Rating(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text = kwargs.get("Text")
        self.places = kwargs.get("places")
        self.rating_info = kwargs.get("rating_info")

        if hasattr(self.text, "formatter"):
            shift = kwargs.get("shift", {})
            TimeTools.set_default_shift(shift)
            date_from = kwargs.get("date_from", "{day_z}.{month_z}.{year}")
            date_to = kwargs.get("date_from", "{day_z}.{month_z}.{year}")
            self.text.formatter = TextInserter(FormatterFunction(self.format_text, period=self.rating_info.period,
                                                                 shift=shift, date_from=date_from, date_to=date_to))

    def draw(self, surface):
        if self.text:
            surface = self.text.draw(surface)
        sort_values = list(self.rating_info.points.values())
        sort_values.sort(key=lambda x: -x[MemberInfoTypes.POINTS.value] if x[MemberInfoTypes.MEMBER_INFO.value]
                                                                           not in self.rating_info.ban_list else 0)
        min_len = min(len(self.places), len(sort_values))
        logger.debug(f"отрисовка рейтинга {self.name}")
        for i in range(min_len):
            mi = sort_values[i] if sort_values[i][MemberInfoTypes.POINTS.value] > 0 else {}
            self.places[i].update_member_info(mi)
            logger.debug(mi)

        surface = reduce(lambda x, y: y.draw(x), self.places, surface)
        return surface

    @staticmethod
    def format_text(period: str, shift: dict, date_from: str, date_to: str) -> typing.Dict[str, str]:
        interval = TimeTools.get_period_interval(period)
        d_fr = date_from.format(**TimeTools.get_shift_and_format_time(
            shift=shift, dtime=datetime.datetime.fromtimestamp(interval.fr)))
        d_to = date_to.format(**TimeTools.get_shift_and_format_time(
            shift=shift, dtime=datetime.datetime.fromtimestamp(interval.to)))
        return {"date_from": d_fr, "date_to": d_to}

    @property
    def places(self) -> typing.List["RatingPlace"]:
        return self._places

    @places.setter
    def places(self, places: typing.List["RatingPlace"]):
        if places and not isinstance(places, list):
            raise exceptions.CreateTypeException("places", list, type(places))
        self._places = places

    @property
    def rating_info(self) -> RatingInfo:
        return self._rating_info

    @rating_info.setter
    def rating_info(self, rating_info: RatingInfo):
        if rating_info and not isinstance(rating_info, RatingInfo):
            raise exceptions.CreateTypeException("rating_info", RatingInfo, type(rating_info))
        self._rating_info = rating_info

    @property
    def text(self) -> Text:
        return self._text

    @text.setter
    def text(self, text: Text):
        if text and not isinstance(text, Text):
            raise exceptions.CreateTypeException("text", Text, type(text))
        self._text = text


class RatingPlace(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.member_info = {}
        self.default_avatar = kwargs.get("default_avatar")
        self.profile = kwargs.get("profile")
        self.profile.info.formatter = TextInserter(FormatterFunction(function=self.get_place_info))

    def draw(self, surface):
        if len(self.member_info) != 0:
            surface = self.profile.draw(surface)
        elif self.default_avatar is not None:
            surface = self.default_avatar.draw(surface)
        return surface

    def update_member_info(self, member_info: typing.Dict[str, int]):
        self.member_info = member_info
        if hasattr(self.profile.avatar, "user_id"):
            self.profile.avatar.user_id = self.member_info.get(MemberInfoTypes.MEMBER_INFO.value)

    def get_place_info(self) -> typing.Dict[str, str]:
        dct = UserInfo.get_user_info(self.member_info[MemberInfoTypes.MEMBER_INFO.value])
        dct.update(self.member_info)
        return dct

    @property
    def profile(self) -> Profile:
        return self._profile

    @profile.setter
    def profile(self, profile: Profile):
        if profile and not isinstance(profile, Profile):
            raise exceptions.CreateTypeException("profile", Profile, type(profile))
        self._profile = profile
