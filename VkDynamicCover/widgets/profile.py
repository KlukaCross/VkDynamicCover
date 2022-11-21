from VkDynamicCover.widgets.widget import Widget
from VkDynamicCover.widgets.message import Message
from VkDynamicCover.widgets.picture import Picture

from VkDynamicCover.utils import widgets, vk_tools


class Profile(Widget):
    def __init__(self):
        super().__init__()
        self._info = None
        self._avatar = None

    def draw(self, surface):
        if not self.user_id:
            return surface
        surface = super().draw(surface)

        if self.avatar:
            surface = self.avatar.draw(surface)
        return surface

    @property
    def info(self) -> Message:
        return self._info

    @info.setter
    def info(self, info: Message):
        self._info = info

    @property
    def avatar(self) -> Picture:
        return self._avatar

    @avatar.setter
    def avatar(self, avatar: Picture):
        self._avatar = avatar

    def get_format_text(self, text) -> str:
        user = vk.get_user(vk_session=self.vk_session, user_id=self.user_id)
        return text.format(first_name=user["first_name"], last_name=user["last_name"])






class RandomAvatar(RandomPicture):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

    def set_user_id(self, user_id):
        self.random_function = lambda x: user_id % x
