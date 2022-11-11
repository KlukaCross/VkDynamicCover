import typing
from VkDynamicCover.types import MemberInfo


class RatingMembers:
    def __init__(self):
        self._rating: typing.Dict[int, MemberInfo] = {}

    def add(self, member_id: int) -> bool:
        if member_id in self._rating:
            return False
        self._rating[member_id] = MemberInfo(member_id=member_id)

    def get_all(self) -> typing.List[MemberInfo]:
        return list(self._rating.values())
