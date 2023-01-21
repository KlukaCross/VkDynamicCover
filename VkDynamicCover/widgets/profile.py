import typing

from VkDynamicCover.text_formatting import TextInserter
from VkDynamicCover.widgets.text import FormattingText
from VkDynamicCover.widgets.widget import Widget
from VkDynamicCover.widgets.picture import Picture
from VkDynamicCover.text_formatting import FormatterFunction
from VkDynamicCover.types import exceptions

from VkDynamicCover.utils import VkTools


class Profile(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info = kwargs.get("info")
        self.avatar = kwargs.get("avatar")

    def draw(self, surface):
        if self.info:
            surface = self.info.draw(surface)
        if self.avatar:
            surface = self.avatar.draw(surface)
        return surface

    @property
    def info(self) -> "UserInfo":
        return self._info

    @info.setter
    def info(self, info: "UserInfo"):
        if info and not isinstance(info, UserInfo):
            raise exceptions.CreateTypeException("info", UserInfo, type(info))
        self._info = info

    @property
    def avatar(self) -> Picture:
        return self._avatar

    @avatar.setter
    def avatar(self, avatar: Picture):
        if avatar and not isinstance(avatar, Picture):
            raise exceptions.CreateTypeException("avatar", Picture, type(avatar))
        self._avatar = avatar


class UserInfo(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text: FormattingText = kwargs.get("text")
        self.user_id = kwargs.get("user_id")
        self.text.formatter = TextInserter(FormatterFunction(UserInfo.get_user_info, user_id=self.user_id))

    def draw(self, surface):
        return self.text.draw(surface)

    @staticmethod
    def get_user_info(user_id: int) -> typing.Dict[str, str]:
        user_info = VkTools.get_user(user_id=user_id)
        return user_info

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int):
        if user_id and not isinstance(user_id, int):
            raise exceptions.CreateTypeException("user_id", int, type(user_id))
        self._user_id = user_id

    @property
    def formatter(self):
        return self.text.formatter

    @formatter.setter
    def formatter(self, formatter):
        self.text.formatter = formatter
