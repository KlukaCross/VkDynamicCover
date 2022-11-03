from VkDynamicCover.widgets import text_set, picture

from VkDynamicCover.utils import widgets, vk


class Profile(text_set.TextSet, picture.Picture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.crop_type = kwargs.get("crop_type", "crop")

        self.user_id = kwargs.get("user_id")

        self.default_path = kwargs.get("default_path", None)
        self.default_url = kwargs.get("default_url", None)

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

    def get_image(self):

        if self.path:
            p = Path(self.path)
            return draw.get_image_from_path(p)
        if self.url:
            return draw.get_image_from_url(self.url)

        if not self.user_id:
            return self.default_picture.get_image()

        user = vk.get_user(vk_session=self.vk_session, user_id=self.user_id, fields="crop_photo")

        if "crop_photo" not in user:
            return self.default_picture.get_image()

        sizes = user["crop_photo"]["photo"]["sizes"]
        photo_max = 0
        for i in range(len(sizes)):
            if sizes[i]["width"] > sizes[photo_max]["width"]:
                photo_max = i

        photo = draw.get_image_from_url(sizes[photo_max]["url"])

        if self.crop_type in ["crop", "small"]:
            photo = photo.crop((photo.width * user["crop_photo"]["crop"]["x"] // 100,
                                photo.height * user["crop_photo"]["crop"]["y"] // 100,
                                photo.width * user["crop_photo"]["crop"]["x2"] // 100,
                                photo.height * user["crop_photo"]["crop"]["y2"] // 100))
            if self.crop_type == "small":
                photo = photo.crop((photo.width * user["crop_photo"]["rect"]["x"] // 100,
                                    photo.height * user["crop_photo"]["rect"]["y"] // 100,
                                    photo.width * user["crop_photo"]["rect"]["x2"] // 100,
                                    photo.height * user["crop_photo"]["rect"]["y2"] // 100))

        return photo

    def set_user_id(self, user_id):
        self.user_id = user_id
        if self.avatar:
            self.avatar.user_id = user_id


class Avatar(Picture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.crop_type = kwargs.get("crop_type", "crop")

        self.user_id = kwargs.get("user_id")

        def_pic = {"name": "Picture", "path": kwargs.get("default_path"), "url": kwargs.get("default_url")}
        self.default_picture = widgets.create_widget(config, **def_pic)



class RandomAvatar(RandomPicture):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

    def set_user_id(self, user_id):
        self.random_function = lambda x: user_id % x
