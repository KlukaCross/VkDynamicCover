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


class Rating(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.text = kwargs.get("Text", None)
        self.places = kwargs.get("places")
        self.rating_info = kwargs.get("rating_info")

    def draw(self, surface):
        if self.text:
            surface = self.text.draw(surface)
        sort_values = list(self.rating_info.points.values())
        sort_values.sort(key=lambda x: -x["points"])
        min_len = min(len(self.places), len(sort_values))
        for i in range(min_len):
            self.places[i].update_member_info(sort_values[i])
        surface = reduce(lambda x, y: y.draw(x), self.places, surface)
        return surface

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
        self.profile = kwargs.get("profile")
        self.profile.info.formatter = TextInserter(FormatterFunction(function=self.get_place_info))

    def draw(self, surface):
        if len(self.member_info) != 0:
            surface = self.profile.draw(surface)
        return surface

    def update_member_info(self, member_info: typing.Dict[str, int]):
        self.member_info = member_info
        if hasattr(self.profile.avatar, "user_id"):
            self.profile.avatar.user_id = self.member_info[MemberInfoTypes.MEMBER_INFO.value]

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
