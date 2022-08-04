from VkDynamicCover.widgets.text_set import TextSet

from ..utils import widgets, vk


class Profile(TextSet):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        self.crop_type = kwargs.get("crop_type", "crop")

        self.user_id = kwargs.get("user_id")

        avatar = kwargs.get("avatar", {})
        avatar["name"] = "Avatar"
        self.avatar = widgets.create_widget(config, **avatar) if "avatar" in kwargs else None

    def draw(self, surface):
        if not self.user_id:
            return surface
        surface = super().draw(surface)

        if self.avatar:
            surface = self.avatar.draw(surface)
        return surface

    def get_format_text(self, text) -> str:
        user = vk.get_user(vk_session=self.vk_session, user_id=self.user_id)
        return text.format(first_name=user["first_name"], last_name=user["last_name"])

    def set_user_id(self, user_id):
        self.user_id = user_id
        if self.avatar:
            self.avatar.user_id = user_id
