import typing
from VkDynamicCover.types import MemberInfo


class RatingMembers:
    def __init__(self):
        self._rating: typing.Dict[int, MemberInfo] = {}

    def add(self, member_id: int) -> MemberInfo:
        if member_id in self._rating:
            return self._rating[member_id]
        member_info = MemberInfo(member_id=member_id)
        self._rating[member_id] = member_info
        return member_info

    def get_member(self, member_id: int) -> MemberInfo or None:
        return self._rating.get(member_id)

    def get_all(self) -> typing.List[MemberInfo]:
        return list(self._rating.values())
