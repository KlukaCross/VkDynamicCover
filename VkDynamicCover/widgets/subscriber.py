import datetime
from copy import copy
from functools import reduce

from apscheduler.schedulers.background import BackgroundScheduler
from vk_api.bot_longpoll import VkBotEventType
from loguru import logger

from .widget import Widget
from .text_set import TextSet
from .picture import Picture

from ..utils import vk, draw

MEMBER_RATING = {"likes": 0, "comments": 0, "reposts": 0}


class Subscriber(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.period = kwargs.get("period", "month")
        self.rating_period = self.get_rating_period()
        self.group_id = kwargs.get("group_id") or self.group_id

        self.point_weights = kwargs.get("point_weights", {
            "likes": 0,
            "reposts": 0,
            "comments": 0
        })
        self.like_places = [MemberPlace(**kwargs, **p) for p in kwargs.get("like_places", [])]
        self.repost_places = [MemberPlace(**kwargs, **p) for p in kwargs.get("repost_places", [])]
        self.comment_places = [MemberPlace(**kwargs, **p) for p in kwargs.get("comment_places", [])]
        self.point_places = [MemberPlace(**kwargs, **p) for p in kwargs.get("point_places", [])]
        self.lastSub_places = [MemberPlace(**kwargs, **p) for p in kwargs.get("lastSub_places", [])]

        self.rating = {}

        self.init_rating()
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=vk.longpoll_listener,
            kwargs={
                "vk_session": self.vk_session,
                "group_id": self.group_id,
                "callback": self.longpoll_update}
        )
        self.scheduler.start()

    def draw(self, surface):
        self.update_rating()

        surface = reduce(lambda x, y: y.draw(x), self.like_places, surface)
        surface = reduce(lambda x, y: y.draw(x), self.repost_places, surface)
        surface = reduce(lambda x, y: y.draw(x), self.comment_places, surface)
        surface = reduce(lambda x, y: y.draw(x), self.point_places, surface)
        surface = reduce(lambda x, y: y.draw(x), self.lastSub_places, surface)

        return surface

    def get_rating_period(self) -> (int, int):
        tmp = datetime.datetime.now()
        if self.period == "day":
            fr = tmp.replace(hour=0, minute=0, second=0)
            to = datetime.timedelta(days=1) + fr
        elif self.period == "week":
            fr = tmp.replace(hour=0, minute=0, second=0) - datetime.timedelta(days=tmp.weekday())
            to = datetime.timedelta(days=7) + fr
        elif self.period == "month":
            fr = tmp.replace(day=1, hour=0, minute=0, second=0)
            to = fr.replace(year=fr.year + 1, month=1) if fr.month == 12 else fr.replace(month=fr.month + 1)
        elif self.period == "year":
            fr = tmp.replace(month=1, day=1, hour=0, minute=0, second=0)
            to = fr.replace(year=fr.year + 1)
        else:
            logger.warning(f"Неизвестный период - {self.period}")
            return [0, 0]
        return int(fr.timestamp()), int(to.timestamp())

    def init_rating(self):
        logger.info("Инициализируется рейтинг для виджета subscriber...")
        posts = vk.get_posts_from_date(vk_session=self.vk_session,
                                       group_id=self.group_id,
                                       from_date_unixtime=self.rating_period[0])

        for p in posts:
            likes = vk.get_post_liker_ids(vk_session=self.vk_session,
                                          group_id=self.group_id,
                                          post_id=p["id"],
                                          likes_count=p["likes"]["count"])
            comments = vk.get_post_comments(vk_session=self.vk_session,
                                            group_id=self.group_id,
                                            post_id=p["id"],
                                            comments_count=p["comments"]["count"])
            reposts = vk.get_post_reposts(vk_session=self.vk_session,
                                          group_id=self.group_id,
                                          post_id=p["id"],
                                          reposts_count=p["reposts"]["count"])

            for i in likes:
                self.rating.setdefault(i, copy(MEMBER_RATING))["likes"] += 1

            for i in comments:
                self.rating.setdefault(i["from_id"], copy(MEMBER_RATING))["comments"] += 1

            for i in reposts:
                self.rating.setdefault(i["from_id"], copy(MEMBER_RATING))["reposts"] += 1
        logger.info(f"Инициализация рейтинга завершена.")

    def update_rating(self):
        def upd(places, func_key):
            if len(places) <= 0 or len(self.rating) <= 0:
                return

            top = list(filter(lambda x: func_key(x) > 0, self.rating.keys()))
            top.sort(key=func_key, reverse=True)

            to = min(len(places), len(top))
            for i in range(to):
                user_rating = self.rating[top[i]]
                user_rating["points"] = self.calc_points(top[i])
                places[i].update_place(top[i], user_rating)

        if self.is_reset_rating():
            logger.info("Сброс рейтинга")
            self.rating.clear()
            self.init_rating()

        upd(self.like_places, lambda x: self.rating[x]["likes"])
        upd(self.repost_places, lambda x: self.rating[x]["reposts"])
        upd(self.comment_places, lambda x: self.rating[x]["comments"])
        upd(self.point_places, self.calc_points)

    def calc_points(self, user_id):
        return self.rating[user_id]["likes"] * self.point_weights.get("likes", 0) + \
               self.rating[user_id]["comments"] * self.point_weights.get("comments", 0) + \
               self.rating[user_id]["reposts"] * self.point_weights.get("reposts", 0)

    def is_reset_rating(self) -> bool:
        return datetime.datetime.now().timestamp() > self.rating_period[1]

    def longpoll_update(self, event):
        if event.type == VkBotEventType.WALL_REPLY_NEW:
            if not self.is_valid_post(event.object["post_id"]):
                return
            self.rating.setdefault(event.object["from_id"], MEMBER_RATING)["comments"] += 1
            return

        if event.type in [
            "like_add",
            "like_remove"
        ]:
            if event.object["object_owner_id"] != self.group_id or \
                    not self.is_valid_post(event.object["object_id"]):
                return
            if event.type == "like_add":
                self.rating.setdefault(event.object["liker_id"], MEMBER_RATING)["likes"] += 1
            else:
                self.rating.setdefault(event.object["liker_id"], MEMBER_RATING)["likes"] -= 1
            return

        if event.type == VkBotEventType.WALL_REPOST:
            if not self.is_valid_post(event.object["id"]):
                return
            self.rating.setdefault(event.object["owner_id"], MEMBER_RATING)["reposts"] -= 1

    def is_valid_post(self, post_id) -> bool:
        post = vk.get_post(vk_session=self.vk_session, group_id=self.group_id, post_id=post_id)
        return post["date"] < self.rating_period[1]


class MemberPlace(TextSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ava = kwargs.get("avatar", None)
        if ava:
            kwargs.pop("xy", None)
            self.avatar = Avatar(**ava, **kwargs)
        else:
            self.avatar = None

        self.member_id = -1
        self.member_rating: dict = {}

    def draw(self, surface):
        surface = super().draw(surface)
        if self.avatar:
            surface = self.avatar.draw(surface)
        return surface

    def get_format_text(self, text):
        if self.member_id < 0:
            return ""
        user = vk.get_user(vk_session=self.vk_session, user_id=self.member_id)
        return text.format(first_name=user["first_name"],
                           last_name=user["last_name"],
                           likes=self.member_rating["likes"],
                           comments=self.member_rating["comments"],
                           reposts=self.member_rating["reposts"],
                           points=self.member_rating["points"])

    def update_place(self, member_id, member_rating: dict):
        self.member_id = member_id
        self.member_rating = member_rating
        if self.avatar:
            self.avatar.member_id = member_id


class Avatar(Picture):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.crop_type = kwargs.get("crop_type", "crop")

        default_kwargs = {**kwargs, "path": kwargs.get("default_path"), "url": kwargs.get("default_url")}
        self.default_picture = Picture(**default_kwargs)

        self.random_images_path = kwargs.get("random_images_path", None)

        self.member_id = -1

    def get_image(self):
        if self.member_id < 0:
            return self.default_picture.get_image()

        if self.random_images_path:
            return draw.get_random_image_from_dir(self.random_images_path)

        user = vk.get_user(vk_session=self.vk_session, user_id=self.member_id, fields="crop_photo")

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
