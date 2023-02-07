import datetime
import typing
from functools import reduce

from PIL.Image import Image

from .profile import UserInfoInfo
from .text import TextControl
from .widget import WidgetControl, WidgetInfo, WidgetDrawer, WidgetDesigner
from .profile import ProfileControl
from VkDynamicCover.text_formatting import FormatterFunction
from VkDynamicCover.text_formatting import TextInserter
from VkDynamicCover.rating_handler.rating_unit_info import RatingUnitInfo
from VkDynamicCover.types import exceptions, MemberInfoTypes
from VkDynamicCover.utils import TimeTools

from loguru import logger


class RatingControl(WidgetControl):
    __TYPE__ = "Rating"


class RatingDrawer(WidgetDrawer):
    def draw(self, surface: Image, info: "RatingInfo") -> Image:
        if info.text:
            surface = info.text.draw(surface)
        surface = reduce(lambda x, y: y.draw(x), info.places, surface)
        return surface


class RatingDesigner(WidgetDesigner):
    def design(self, info: "RatingInfo"):
        sort_values = list(info.rating_info.points.values())
        sort_values.sort(key=lambda x: -x[MemberInfoTypes.POINTS.value] if x[MemberInfoTypes.MEMBER_INFO.value]
                                                                           not in info.rating_info.ban_list else 0)
        min_len = min(len(info.places), len(sort_values))
        for i in range(min_len):
            mi = sort_values[i] if sort_values[i][MemberInfoTypes.POINTS.value] > 0 else {}
            info.places[i].designer.update_member_info(info.places[i].info, mi)
            logger.debug(mi)


class RatingInfo(WidgetInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text = kwargs.get("text")
        self.places = kwargs.get("places")
        self.rating_info = kwargs.get("rating_info")

        if hasattr(self.text, "formatter"):
            shift = kwargs.get("shift", {})
            TimeTools.set_default_shift(shift)
            date_from = kwargs.get("date_from", "{day_z}.{month_z}.{year}")
            date_to = kwargs.get("date_from", "{day_z}.{month_z}.{year}")
            self.text.formatter = TextInserter(FormatterFunction(self.format_text, period=self.rating_info.period,
                                                                 shift=shift, date_from=date_from, date_to=date_to))

    @staticmethod
    def format_text(period: str, shift: dict, date_from: str, date_to: str) -> typing.Dict[str, str]:
        interval = TimeTools.get_period_interval(period)
        d_fr = date_from.format(**TimeTools.get_shift_and_format_time(
            shift=shift, dtime=datetime.datetime.fromtimestamp(interval.fr)))
        d_to = date_to.format(**TimeTools.get_shift_and_format_time(
            shift=shift, dtime=datetime.datetime.fromtimestamp(interval.to)))
        return {"date_from": d_fr, "date_to": d_to}

    @property
    def places(self) -> typing.List["RatingPlaceControl"]:
        return self._places

    @places.setter
    def places(self, places: typing.List["RatingPlaceControl"]):
        if places and not isinstance(places, list):
            raise exceptions.CreateTypeException("places", list, type(places))
        self._places = places

    @property
    def rating_info(self) -> RatingUnitInfo:
        return self._rating_info

    @rating_info.setter
    def rating_info(self, rating_info: RatingUnitInfo):
        if rating_info and not isinstance(rating_info, RatingUnitInfo):
            raise exceptions.CreateTypeException("rating_info", RatingUnitInfo, type(rating_info))
        self._rating_info = rating_info

    @property
    def text(self) -> TextControl:
        return self._text

    @text.setter
    def text(self, text: TextControl):
        if text and not isinstance(text, TextControl):
            raise exceptions.CreateTypeException("text", TextControl, type(text))
        self._text = text


class RatingPlaceControl(WidgetControl):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info.profile.info_text.formatter = TextInserter(FormatterFunction(function=self.info.get_place_info))


class RatingPlaceDrawer(WidgetDrawer):
    def draw(self, surface: Image, info: "RatingPlaceInfo") -> Image:
        if len(info.member_info) != 0:
            surface = info.profile.draw(surface)
        elif info.default_avatar is not None:
            surface = info.default_avatar.draw(surface)
        return surface


class RatingPlaceDesigner(WidgetDesigner):
    def design(self, info: "RatingPlaceInfo"):
        pass

    def update_member_info(self, info: "RatingPlaceInfo", member_info: typing.Dict[str, int]):
        info.member_info = member_info
        if hasattr(info.profile.avatar, "user_id"):
            info.profile.avatar.user_id = info.member_info.get(MemberInfoTypes.MEMBER_INFO.value)


class RatingPlaceInfo(WidgetInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.member_info = {}
        self.default_avatar = kwargs.get("default_avatar")
        self.profile = kwargs.get("profile")

    def get_place_info(self) -> typing.Dict[str, str]:
        dct = UserInfoInfo.get_user_info(self.member_info[MemberInfoTypes.MEMBER_INFO.value])
        dct.update(self.member_info)
        return dct

    @property
    def profile(self) -> ProfileControl:
        return self._profile

    @profile.setter
    def profile(self, profile: ProfileControl):
        if profile and not isinstance(profile, ProfileControl):
            raise exceptions.CreateTypeException("profile", ProfileControl, type(profile))
        self._profile = profile
