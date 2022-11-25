import typing

from VkDynamicCover.widgets.text import Text, FormattingText
from VkDynamicCover.widgets.widget import Widget
from VkDynamicCover.widgets.picture import Picture
from VkDynamicCover.helpers.text_formatting.text_formatter import TextFormatter, FormatterFunction

from VkDynamicCover.utils import widgets, vk_tools, VkTools


class Profile(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info = kwargs.get("info")
        self.avatar = kwargs.get("avatar")

    def draw(self, surface):
        if not self.info:
            return surface
        surface = super().draw(surface)

        if self.avatar:
            surface = self.avatar.draw(surface)
        return surface

    @property
    def info(self) -> Text:
        return self._info

    @info.setter
    def info(self, info: Text):
        self._info = info

    @property
    def avatar(self) -> Picture:
        return self._avatar

    @avatar.setter
    def avatar(self, avatar: Picture):
        self._avatar = avatar


class UserInfo(FormattingText):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = kwargs.get("user_id")
        self.formatter = TextFormatter(FormatterFunction(UserInfo.get_user_info, user_id=self.user_id))

    @staticmethod
    def get_user_info(user_id: int) -> typing.Dict[str, str]:
        user_info = VkTools.get_user(user_id=user_id)
        return user_info

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int):
        self._user_id = user_id
