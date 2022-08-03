import datetime
from functools import reduce

from apscheduler.schedulers.background import BackgroundScheduler
from vk_api.bot_longpoll import VkBotEventType
from loguru import logger

from .widget import Widget

from ..utils import vk, draw, widgets
from ..utils.widgets.other import MemberPlace

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

        period_info = kwargs.get("period_info")
        self.period_info = widgets.create_widget(period_info, name="PeriodInfo") if period_info else None
        if period_info:
            self.period_info.set_period(time_from=datetime.datetime.fromtimestamp(self.rating_period[0]),
                                        time_to=datetime.datetime.fromtimestamp(self.rating_period[1]))

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
                self.rating.setdefault(i, MEMBER_RATING.copy())["likes"] += 1

            for i in comments:
                self.rating.setdefault(i["from_id"], MEMBER_RATING.copy())["comments"] += 1

            for i in reposts:
                self.rating.setdefault(i["from_id"], MEMBER_RATING.copy())["reposts"] += 1
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
            if self.period_info:
                self.period_info.set_period(time_from=datetime.datetime.fromtimestamp(self.rating_period[0]),
                                            time_to=datetime.datetime.fromtimestamp(self.rating_period[1]))

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
            self.rating.setdefault(event.object["from_id"], MEMBER_RATING.copy())["comments"] += 1
            return

        if event.type in [
            "like_add",
            "like_remove"
        ]:
            if event.object["object_owner_id"] != self.group_id or \
                    not self.is_valid_post(event.object["object_id"]):
                return
            if event.type == "like_add":
                self.rating.setdefault(event.object["liker_id"], MEMBER_RATING.copy())["likes"] += 1
            else:
                self.rating.setdefault(event.object["liker_id"], MEMBER_RATING.copy())["likes"] -= 1
            return

        if event.type == VkBotEventType.WALL_REPOST:
            if not self.is_valid_post(event.object["id"]):
                return
            self.rating.setdefault(event.object["owner_id"], MEMBER_RATING.copy())["reposts"] -= 1

    def is_valid_post(self, post_id) -> bool:
        post = vk.get_post(vk_session=self.vk_session, group_id=self.group_id, post_id=post_id)
        return post["date"] < self.rating_period[1]


