from VkDynamicCover.helpers.rating.rating_members import RatingMembers
from VkDynamicCover.types import MetaSingleton, MemberInfo
from VkDynamicCover.listeners import Subscriber
import typing

from VkDynamicCover.types.interval import Interval


class RatingHandler(metaclass=MetaSingleton, Subscriber):
    def __init__(self):
        self._ratings: typing.Dict[Interval, RatingMembers]
        self._is_updating: typing.Dict[Interval, bool]
        self._ban_ids: typing.Dict[Interval, typing.List[int]]

    def update(self, event):
        pass

    def add_rating(self, interval: Interval, ban_list: typing.List[int]):
        pass

    def del_rating(self, interval: Interval):
        pass

    def get_top(self, interval: Interval, formula: str, top_count: int) -> typing.List[MemberInfo]:
        pass

    def calc_points(self, member: MemberInfo, formula: str):
        pass
