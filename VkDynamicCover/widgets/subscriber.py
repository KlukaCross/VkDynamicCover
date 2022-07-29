import math
import datetime
import time

from apscheduler.schedulers.background import BackgroundScheduler
from vk_api.bot_longpoll import VkBotEventType

from .widget import Widget
from .text import Text
from .picture import Picture

from ..utils import vk, draw

MEMBER_RATING = {"likes": 0, "comments": 0, "reposts": 0}


class Subscriber(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, **kwargs)

        self.period = kwargs.get("period", "month")
        self.start_period = self.get_start_period()

        self.point_weights = kwargs.get("point_weights", {
            "likes": 0,
            "reposts": 0,
            "comments": 0
        })
        self.like_places = [MemberPlace(vk_session=self.vk_session, **p) for p in kwargs.get("like_places", [])]
        self.repost_places = [MemberPlace(vk_session=self.vk_session, **p) for p in kwargs.get("repost_places", [])]
        self.comment_places = [MemberPlace(vk_session=self.vk_session, **p) for p in kwargs.get("comment_places", [])]
        self.point_places = [MemberPlace(vk_session=self.vk_session, **p) for p in kwargs.get("point_places", [])]
        self.lastSub_places = [MemberPlace(vk_session=self.vk_session, **p) for p in kwargs.get("lastSub_places", [])]

        self.rating = {}

        self.init_rating()
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=vk.longpoll_listener,
            kwargs={
                "group_id": self.config["group_id"],
                "callback": self.longpoll_update}
        )
        self.scheduler.start()

    def draw(self, surface):
        self.update_rating()

        map(lambda x: x.draw(surface), self.like_places)
        map(lambda x: x.draw(surface), self.repost_places)
        map(lambda x: x.draw(surface), self.comment_places)
        map(lambda x: x.draw(surface), self.point_places)
        map(lambda x: x.draw(surface), self.lastSub_places)

        return surface

    def get_start_period(self) -> int:
        tmp = datetime.datetime.now()
        if self.period == "day":
            tmp = tmp.replace(hour=0, minute=0, second=0)
            return math.trunc(datetime.timedelta(seconds=tmp.timestamp()).total_seconds())
        if self.period == "week":
            tmp = tmp.replace(hour=0, minute=0, second=0)
            return math.trunc(datetime.timedelta(days=tmp.toordinal() - tmp.weekday()).total_seconds())
        if self.period == "month":
            tmp = tmp.replace(day=0, hour=0, minute=0, second=0)
            return math.trunc(datetime.timedelta(seconds=tmp.timestamp()).total_seconds())
        if self.period == "year":
            tmp = tmp.replace(month=0, day=0, hour=0, minute=0, second=0)
            return math.trunc(datetime.timedelta(tmp.timestamp()).total_seconds())

    def init_rating(self):
        posts = vk.get_posts_from_date(vk_session=self.vk_session,
                                       group_id=self.config["group_id"],
                                       from_date_unixtime=self.start_period)
        for p in posts:
            likes = vk.get_post_liker_ids(vk_session=self.vk_session,
                                          group_id=self.config["group_id"],
                                          post_id=p["id"],
                                          likes_count=p["likes"]["count"])
            comments = vk.get_post_comments(vk_session=self.vk_session,
                                            group_id=self.config["group_id"],
                                            post_id=p["id"],
                                            comments_count=p["comments"]["count"])
            reposts = vk.get_post_reposts(vk_session=self.vk_session,
                                          group_id=self.config["group_id"],
                                          post_id=p["id"],
                                          reposts_count=p["reposts"]["count"])

            for i in likes:
                self.rating.setdefault(i, MEMBER_RATING)["likes"] += 1

            for i in comments:
                self.rating.setdefault(i, MEMBER_RATING)["comments"] += 1

            for i in reposts:
                self.rating.setdefault(i, MEMBER_RATING)["reposts"] += 1

    def update_rating(self):
        def upd(lst, key, func=None):
            if len(lst) <= 0:
                return
            if not func:
                func = lambda k: self.rating[k][key]
            top = list(self.rating.keys())
            top.sort(key=func)
            for i in range(len(lst)):
                user_rating = self.rating[top[i]]
                user_rating["points"] = self.calc_points(top[i])
                lst[i].update_place(top[i], user_rating)

        if self.is_reset_rating():
            self.rating.clear()
            self.init_rating()

        upd(self.like_places, "likes")
        upd(self.repost_places, "reposts")
        upd(self.comment_places, "comments")
        upd(self.point_places, "point", self.calc_points)

    def calc_points(self, user_id):
        return self.rating[user_id]["likes"] * self.point_weights["likes"] + \
               self.rating[user_id]["comments"] * self.point_weights["comments"] + \
               self.rating[user_id]["reposts"] * self.point_weights["reposts"]

    def is_reset_rating(self) -> bool:
        if self.period == "day":
            return time.gmtime().tm_mday != time.gmtime(self.start_period).tm_mday
        if self.period == "week":
            return time.gmtime().tm_wday != time.gmtime(self.start_period).tm_wday
        if self.period == "month":
            return time.gmtime().tm_mon != time.gmtime(self.start_period).tm_mon
        if self.period == "year":
            return time.gmtime().tm_year != time.gmtime(self.start_period).tm_year

    def longpoll_update(self, event):
        if event.type in [
            VkBotEventType.WALL_REPLY_NEW,
            VkBotEventType.WALL_REPLY_DELETE,
            VkBotEventType.WALL_REPLY_RESTORE
        ]:
            if not self.is_valid_post(event.object["post_id"]):
                return
            if event.type == VkBotEventType.WALL_REPLY_DELETE:
                self.rating.setdefault(event.object["from_id"], MEMBER_RATING)["comments"] -= 1
            else:
                self.rating.setdefault(event.object["from_id"], MEMBER_RATING)["comments"] += 1
            return

        if event.type in [
            "like_add",
            "like_remove"
        ]:
            if event.object["object_owner_id"] != self.config["group_id"] or \
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
        post = vk.get_post(vk_session=self.vk_session, group_id=self.config["group_id"], post_id=post_id)
        return post["date example"] >= self.start_period


class MemberPlace(Text, Picture):
    def __init__(self, **kwargs):
        self.picture = kwargs.get("picture", {})
        self.format = kwargs.get("format", "{first_name} {last_name}")

        self.member_id = -1
        self.member_rating: dict = {}

        Text.__init__(**kwargs)
        Picture.__init__(**kwargs)

    def draw(self, surface):
        Text.draw(self, surface)
        Picture.draw(self, surface)

    def get_text(self) -> str:
        if self.member_id < 0:
            return ""
        user = vk.get_user(vk_session=self.vk_session, user_id=self.member_id)
        return self.format.format(first_name=user["first_name"],
                                  last_name=user["last_name"],
                                  likes=self.member_rating["likes"],
                                  comments=self.member_rating["comments"],
                                  reposts=self.member_rating["reposts"],
                                  points=self.member_rating["points"])

    def get_image(self):
        if self.member_id < 0:
            return
        user = vk.get_user(vk_session=self.vk_session, user_id=self.member_id, fields="crop_photo")

        sizes = user["crop_photo"]["photo"]["sizes"]
        photo_max = 0
        for k, v in sizes.keys():
            if v["width"] > sizes[photo_max]["width"]:
                photo_max = k

        photo = draw.get_image_from_url(sizes[photo_max]["url"])
        photo.crop((photo.width * user["crop_photo"]["crop"]["x"] // 100,
                    photo.height * user["crop_photo"]["crop"]["y"] // 100,
                    photo.width * user["crop_photo"]["crop"]["x2"] // 100,
                    photo.height * user["crop_photo"]["crop"]["y2"] // 100))

        return photo

    def get_resized_image(self, image):
        if "resize" not in self.picture:
            return image
        return image.resize(self.picture["resize"])

    def get_shift(self):
        return self.picture.get("xy", (0, 0))

    def update_place(self, member_id, member_rating: dict):
        self.member_id = member_id
        self.member_rating = member_rating
