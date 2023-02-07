import typing

from PIL.Image import Image

from VkDynamicCover.widgets.text import TextControl
from VkDynamicCover.text_formatting import TextInserter
from VkDynamicCover.widgets.widget import WidgetControl, WidgetDrawer, WidgetInfo, WidgetDesigner
from VkDynamicCover.widgets.picture import PictureControl
from VkDynamicCover.text_formatting import FormatterFunction
from VkDynamicCover.types import exceptions

from VkDynamicCover.utils import VkTools


class ProfileControl(WidgetControl):
    __TYPE__ = "Profile"


class ProfileDrawer(WidgetDrawer):
    def draw(self, surface: Image, info: "ProfileInfo") -> Image:
        if info.info_text:
            surface = info.info_text.draw(surface)
        if info.avatar:
            surface = info.avatar.draw(surface)
        return surface


class ProfileInfo(WidgetInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info_text = kwargs.get("info")
        self.avatar = kwargs.get("avatar")

    @property
    def info_text(self) -> "UserInfoControl":
        return self._info_text

    @info_text.setter
    def info_text(self, info: "UserInfoControl"):
        if info and not isinstance(info, UserInfoControl):
            raise exceptions.CreateTypeException("info", UserInfoControl, type(info))
        self._info_text = info

    @property
    def avatar(self) -> PictureControl:
        return self._avatar

    @avatar.setter
    def avatar(self, avatar: PictureControl):
        if avatar and not isinstance(avatar, PictureControl):
            raise exceptions.CreateTypeException("avatar", PictureControl, type(avatar))
        self._avatar = avatar


class UserInfoControl(WidgetControl):
    __TYPE__ = "UserInfo"


class UserInfoDrawer(WidgetDrawer):
    def draw(self, surface: Image, info: "UserInfoInfo") -> Image:
        return info.text.draw(surface)


class UserInfoInfo(WidgetInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text: TextControl = kwargs.get("text")
        self.user_id = kwargs.get("user_id")
        if hasattr(self.text, "formatter"):
            self.text.formatter = TextInserter(FormatterFunction(self.get_user_info, user_id=self.user_id))

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
