import typing
from functools import reduce

from VkDynamicCover.widgets.profile import Profile, UserInfo

from .text import FormattingText
from .widget import Widget
from VkDynamicCover.helpers.text_formatting.text_formatter import TextFormatter, FormatterFunction
from VkDynamicCover.types.member_info import EasyMemberInfo
from VkDynamicCover.types.rating_info import RatingInfo
from VkDynamicCover.types import exceptions


class Rating(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.places = kwargs.get("places")
        self.rating_info = kwargs.get("rating_info")

    def draw(self, surface):
        sort_values = list(self.rating_info.points.values())
        sort_values.sort()
        for i in range(len(self.places)):
            self.places[i].update_member_info(sort_values[i])
        surface = reduce(lambda x, y: y.draw(x), self.places, surface)
        return surface

    @property
    def places(self) -> typing.List["RatingPlace"]:
        return self._places

    @places.setter
    def places(self, places: typing.List["RatingPlace"]):
        if places and not isinstance(places, list):
            raise exceptions.CreateTypeException(f"places must be list, not {type(places)}")
        self._places = places

    @property
    def rating_info(self) -> RatingInfo:
        return self._rating_info

    @rating_info.setter
    def rating_info(self, rating_info: RatingInfo):
        if rating_info and not isinstance(rating_info, RatingInfo):
            raise exceptions.CreateTypeException(f"rating_info must be RatingInfo, not {type(rating_info)}")
        self._rating_info = rating_info


class RatingPlace(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.profile = kwargs.get("profile")
        self.text = kwargs.get("text")

    def draw(self, surface):
        surface = self.profile.draw(surface)
        surface = self.text.draw(surface)
        return surface

    def update_member_info(self, member_info: EasyMemberInfo):
        self.text.easy_member_info = member_info

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if text and not isinstance(text, RatingPlaceInfo):
            raise exceptions.CreateTypeException(f"text must be RatingPlaceInfo, not {type(text)}")
        self._text = text

    @property
    def profile(self) -> Profile:
        return self._profile

    @profile.setter
    def profile(self, profile: Profile):
        if profile and not isinstance(profile, Profile):
            raise exceptions.CreateTypeException(f"profile must be Profile, not {type(profile)}")
        self._profile = profile


class RatingPlaceInfo(FormattingText):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.easy_member_info = EasyMemberInfo()
        self.formatter = TextFormatter(FormatterFunction(function=RatingPlaceInfo.get_place_info))

    def get_place_info(self) -> typing.Dict[str, str]:
        dct = UserInfo.get_user_info(self.easy_member_info.member_id)
        dct.update({
            "likes": self.easy_member_info.post_likes,
            "comments": self.easy_member_info.post_comments,
            "reposts": self.easy_member_info.reposts,
            "points": self.easy_member_info.points,
            "posts": self.easy_member_info.posts,
            "donates": self.easy_member_info.donates
        })
        return dct
