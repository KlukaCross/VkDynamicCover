from VkDynamicCover.helpers.rating.rating_members import RatingMembers
from VkDynamicCover.types import MetaSingleton, MemberInfo
from VkDynamicCover.listeners import Subscriber
import typing

from VkDynamicCover.types.interval import Interval
from VkDynamicCover.types.rating_info import RatingInfo


class RatingHandler(metaclass=MetaSingleton, Subscriber):
    def __init__(self):
        self._ratings: typing.Dict[Interval, RatingMembers]
        self._is_updating: typing.Dict[Interval, bool]
        self._ban_ids: typing.Dict[Interval, typing.List[int]]

        self.period_info = None
        if period_info:
            period_info["name"] = "PeriodInfo"
            self.period_info = widgets.create_widget(config, **period_info)
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

    def update(self, event):
        pass

    def _update_rating(self):
        def upd(places, func_key):
            if len(places) <= 0 or len(self.rating) <= 0:
                return
            top = list(filter(lambda x: func_key(x) > 0, sorting_keys))
            top.sort(key=func_key, reverse=True)
            to = min(len(places), len(top))
            for i in range(to):
                user_rating = self.rating[top[i]]
                places[i].update_place(top[i], user_rating)
        if self.is_reset_rating():
            logger.info("Сброс рейтинга")
            self.rating.clear()
            self.init_rating()
            if self.period_info:
                self.period_info.set_period(time_from=datetime.datetime.fromtimestamp(self.rating_period[0]),
                                            time_to=datetime.datetime.fromtimestamp(self.rating_period[1]))
        sorting_keys = list(self.rating.keys())
        sorting_keys.sort(key=lambda x: self.rating[x]["points"], reverse=True)
        upd(self.like_places, lambda x: self.rating[x]["likes"])
        upd(self.repost_places, lambda x: self.rating[x]["reposts"])
        upd(self.comment_places, lambda x: self.rating[x]["comments"])
        upd(self.post_places, lambda x: self.rating[x]["posts"])
        upd(self.point_places, self.calc_points)
        self.update_donates()
        upd(self.donate_places, lambda x: self.rating[x]["donates"])

    def _calc_points(self, user_id):
        return self.rating[user_id]["likes"] * self.point_weights.get("likes", 0) + \
               self.rating[user_id]["comments"] * self.point_weights.get("comments", 0) + \
               self.rating[user_id]["reposts"] * self.point_weights.get("reposts", 0) + \
               self.rating[user_id]["posts"] * self.point_weights.get("posts", 0)

    def add_rating(self, rating_info: RatingInfo):
        self.rating_info.append(rating_info)
        pass

    def _get_top(self, interval: Interval, formula: str, top_count: int) -> typing.List[MemberInfo]:
        pass

    def _calc_points(self, member: MemberInfo, formula: str):
        pass

    def _set_period_interval(self) -> (int, int):
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
            fr = to = 0
        self._unixtime_interval = Interval(int(fr.timestamp()), int(to.timestamp()))

    def init_rating(self):
        logger.info("Инициализируется рейтинг для виджета subscriber...")
        posts = VkTools.get_posts_from_date(group_id=self.group_id, from_date_unixtime=self._unixtime_interval.fr)

        for p in posts:
            logger.debug(f"Сбор информации о посте {p['id']}...")
            likes = VkTools.get_post_liker_ids(group_id=self.group_id, post_id=p["id"], likes_count=p["likes"]["count"])
            comments = VkTools.get_post_comments(group_id=self.group_id, post_id=p["id"], comments_count=p["comments"]["count"])
            reposts = VkTools.get_post_reposts(group_id=self.group_id, post_id=p["id"], reposts_count=p["reposts"]["count"])

            for i in likes:
                self.add_point(i, "likes", 1)

            for i in comments:
                self.add_point(i["from_id"], "comments", 1)

            for i in reposts:
                self.add_point(i["from_id"], "reposts", 1)

            self.add_point(p.get("signer_id", -1), "posts", 1)

        if self.donate_places:
            self.update_donates()

        if self.lastSub_places:
            self.update_last_subs()

        logger.info(f"Инициализация рейтинга завершена.")


    def is_reset_rating(self) -> bool:
        return datetime.datetime.now().timestamp() > self.rating_period[1]

    def longpoll_update(self, event):
        logger.debug(f"Новое событие {event}")
        if event.type == VkBotEventType.WALL_REPLY_NEW:
            if not self.is_valid_post(event.object["post_id"]):
                return
            self.add_point(event.object["from_id"], "comments", 1)
            return

        if event.type in [
            "like_add",
            "like_remove"
        ]:
            if event.object["object_owner_id"] != self.group_id or \
                    event.object["object_type"] != "post" or \
                    not self.is_valid_post(event.object["object_id"]):
                return
            point = 1 if event.type == "like_add" else -1
            self.add_point(event.object["liker_id"], "likes", point)
            return

        if event.type == VkBotEventType.WALL_REPOST:
            if not self.is_valid_post(event.object["copy_history"][0]["id"]):
                return
            self.add_point(event.object["owner_id"], "reposts", 1)
            return

        if event.type == VkBotEventType.WALL_POST_NEW:
            if not self.is_valid_post(event.object["id"]):
                return
            self.add_point(event.object.get("signer_id", -1), "posts", 1)
            return

        if event.type == VkBotEventType.GROUP_JOIN:
            self.update_last_subs()
            return

    def is_valid_post(self, post_id) -> bool:
        post = vk.get_post(vk_session=self.vk_session, group_id=self.group_id, post_id=post_id)
        if post:
            return post["date"] >= self.rating_period[0]
        logger.warning(f"invalid post {self.group_id}_{post_id}")
        return False

    def add_point(self, user_id, rating_type, count_points) -> bool:
        if user_id in self.ban_list or user_id < 0:
            return False
        logger.debug(f"Пользователю {user_id} добавлено {count_points} очков к полю {rating_type}")
        self.rating.setdefault(user_id, MEMBER_RATING.copy())[rating_type] += count_points
        self.rating[user_id]["points"] = self.calc_points(user_id)
        return True

    @logger.catch(reraise=False)
    def update_donates(self):
        if not self.donate_key:
            logger.warning("Отсутствует donate_key")
            return

        res = donates.get_donates(key=self.donate_key, count=50)

        if not res["success"]:
            return

        for d in res["donates"]:
            if d["id"] in self.check_donate_ids:
                continue
            self.check_donate_ids.append(d["id"])

            if d["anon"]:
                continue
            if d["ts"] > self.rating_period[0]:
                self.add_point(d["uid"], "donates", d["sum"])

    def update_last_subs(self):
        member_ids = vk.get_group_member_ids(vk_session=self.vk_session,
                                             group_id=self.group_id,
                                             sort="time_desc",
                                             count=len(self.lastSub_places))
        logger.debug(f"Обновлён рейтинг последних подписчиков: {member_ids}")
        for i in range(len(member_ids)):
            self.lastSub_places[i].update_place(member_id=member_ids[i],
                                                member_rating=self.rating.setdefault(member_ids[i],
                                                                                     MEMBER_RATING.copy()))

