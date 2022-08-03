import datetime

from VkDynamicCover.widgets.text_set import TextSet
from .. import time, widgets
from ...widgets.picture import Picture

from .. import vk, draw


class PeriodInfo(TextSet):
    def __init__(self, **kwargs):
        kwargs.update(kwargs.get("texts", {}))
        super().__init__(**kwargs)

        self.text_from = kwargs.get("date_from", "{day}.{month}.{year}")
        self.text_to = kwargs.get("date_to", "{day}.{month}.{year}")

        self.time_from = self.time_to = datetime.datetime.now()

    def get_format_text(self, text) -> str:
        return text.format(date_from=time.format_time(self.time_from, self.text_from),
                           date_to=time.format_time(self.time_to, self.text_to))

    def set_period(self, time_from: datetime.datetime, time_to: datetime.datetime):
        self.time_from = time_from
        self.time_to = time_to


class MemberPlace(TextSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.avatar = kwargs.get("avatar")
        if self.avatar:
            kwargs.pop("xy", None)
            self.avatar = widgets.create_widget(self.avatar, **kwargs, name="Avatar")

        self.profile = widgets.create_widget(kwargs.get("profile", {}), name="Profile")

        self.random_avatar = kwargs.get("random_avatar", None)
        if self.random_avatar:
            self.random_avatar = widgets.create_widget(self.random_avatar, **kwargs,
                                                       name="RandomPicture",
                                                       random_function=lambda count: self.user_id % count)

        self.user_id = None
        self.member_rating: dict = {}

    def draw(self, surface):
        surface = super().draw(surface)
        surface = self.profile.draw(surface)
        if self.random_avatar:
            surface = self.random_avatar.draw(surface)
            return surface
        if self.avatar:
            surface = self.avatar.draw(surface)
        return surface

    def get_format_text(self, text):
        if not self.user_id:
            return ""
        user = vk.get_user(vk_session=self.vk_session, user_id=self.user_id)
        return text.format(first_name=user["first_name"],
                           last_name=user["last_name"],
                           likes=self.member_rating["likes"],
                           comments=self.member_rating["comments"],
                           reposts=self.member_rating["reposts"],
                           points=self.member_rating["points"],
                           donates=self.member_rating["donates"])

    def update_place(self, member_id, member_rating: dict):
        self.user_id = member_id
        self.member_rating = member_rating
        if self.avatar:
            self.avatar.user_id = member_id
        self.profile.set_user_id(member_id)


class Avatar(Picture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.crop_type = kwargs.get("crop_type", "crop")

        self.user_id = kwargs.get("user_id")

        self.default_picture = widgets.create_widget(path=kwargs.get("default_path"),
                                                     url=kwargs.get("default_url"),
                                                     name="Picture", **kwargs)

    def get_image(self):
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
