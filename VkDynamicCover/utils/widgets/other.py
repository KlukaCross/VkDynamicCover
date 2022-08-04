import datetime

from VkDynamicCover.widgets.text_set import TextSet
from .. import time, widgets
from ...widgets.picture import Picture

from .. import vk, draw
from ...widgets.random_picture import RandomPicture


class PeriodInfo(TextSet):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        self.text_from = kwargs.get("date_from", "{day}.{month}.{year}")
        self.text_to = kwargs.get("date_to", "{day}.{month}.{year}")

        self.shift = kwargs.get("shift", {})
        self.shift.setdefault("year", 0)
        self.shift.setdefault("month", 0)
        self.shift.setdefault("week", 0)
        self.shift.setdefault("day", 0)
        self.shift.setdefault("hour", 0)
        self.shift.setdefault("minute", 0)
        self.shift.setdefault("second", 0)

        self.time_from = self.time_to = datetime.datetime.now()

    def get_format_text(self, text) -> str:
        return text.format(date_from=time.format_time(self.time_from, self.text_from),
                           date_to=time.format_time(self.time_to, self.text_to))

    def set_period(self, time_from: datetime.datetime, time_to: datetime.datetime):
        self.time_from = time.shift_time(time_from, self.shift)
        self.time_to = time.shift_time(time_to, self.shift)


class MemberPlace(TextSet):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        profile = kwargs.get("profile")
        profile["name"] = "Profile"
        self.profile = widgets.create_widget(config, **profile)

        random_avatar = kwargs.get("random_avatar", {})
        random_avatar["name"] = "RandomPicture"
        self.random_avatar = RandomAvatar(config, **random_avatar) if "random_avatar" in kwargs else None

        default_image = kwargs.get("default_image", {})
        default_image["name"] = "Picture"
        self.default_image = widgets.create_widget(config, **default_image)

        self.user_id = None
        self.member_rating: dict = {}

    def draw(self, surface):
        surface = super().draw(surface)
        if not self.user_id:
            surface = self.default_image.draw(surface)
            return surface
        surface = self.profile.draw(surface)
        if self.random_avatar:
            surface = self.random_avatar.draw(surface)
            return surface
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
        self.profile.set_user_id(member_id)
        if self.random_avatar:
            self.random_avatar.set_user_id(member_id)


class Avatar(Picture):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        self.crop_type = kwargs.get("crop_type", "crop")

        self.user_id = kwargs.get("user_id")

        def_pic = {"name": "Picture", "path": kwargs.get("default_path"), "url": kwargs.get("default_url")}
        self.default_picture = widgets.create_widget(config, **def_pic)

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


class RandomAvatar(RandomPicture):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

    def set_user_id(self, user_id):
        self.random_function = lambda x: user_id % x
