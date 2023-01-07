import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
from vk_api.bot_longpoll import VkBotEventType

from VkDynamicCover.helpers.rating.rating_members import RatingMembers
from VkDynamicCover.helpers.text_formatting import TextCalculator, FormatterFunction
from VkDynamicCover.types import MetaSingleton, MemberInfo
from VkDynamicCover.listeners import Subscriber
import typing

from VkDynamicCover.types.interval import Interval
from VkDynamicCover.types.member_info import EasyMemberInfo
from VkDynamicCover.types.rating_info import RatingInfo
from VkDynamicCover.types.update_rating_events import UpdateRatingEvents
from VkDynamicCover.utils import VkTools, TimeTools

RATING_UPDATE_SECONDS = 10


class RatingHandler(Subscriber):
    __HANDLERS__ = {}

    def __new__(cls, group_id, *args, **kwargs):
        if group_id not in cls.__HANDLERS__:
            cls.__HANDLERS__[group_id] = super().__new__(cls)
        return cls.__HANDLERS__[group_id]

    def __init__(self, group_id):
        self._group_id = group_id
        self._rating_info: typing.Dict[Interval, typing.List[RatingInfo]] = {}
        self._ratings: typing.Dict[Interval, RatingMembers] = {}
        self._last_subscriber_ids: typing.List[int] = []
        self._max_last_subs: int = 0

        self._formatter_function = FormatterFunction(self.get_formula_member_info)

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=self._update_ratings,
            trigger="interval",
            seconds=RATING_UPDATE_SECONDS
        )
        self.scheduler.start()

    def update(self, event):
        logger.debug(f"Новое событие {event}")
        if event.type == VkBotEventType.WALL_REPLY_NEW:
            self._add_point(user_id=event.object["from_id"],
                            event=UpdateRatingEvents.ADD_COMMENTED_POST,
                            resource=event.object["post_id"],
                            resource_unixtime=VkTools.get_post_time(group_id=self._group_id,
                                                                    post_id=event.object["post_id"]))

        elif event.type in ("like_add", "like_remove"):
            if abs(event.object["object_owner_id"]) != self._group_id:  # чужие посты не считаются
                return
            object_type = event.object["object_type"]
            if object_type == "post":
                update_event = UpdateRatingEvents.ADD_LIKED_POST if event.type == "like_add" else UpdateRatingEvents.DEL_LIKED_POST
                resource_time = VkTools.get_post_time(group_id=self._group_id, post_id=event.object["object_id"])
            elif object_type == "comment":
                update_event = UpdateRatingEvents.ADD_LIKED_COMMENT if event.type == "like_add" else UpdateRatingEvents.DEL_LIKED_COMMENT
                resource_time = VkTools.get_post_time(group_id=self._group_id, post_id=event.object["post_id"])
            else:
                return
            self._add_point(user_id=event.object["liker_id"],
                            event=update_event,
                            resource=event.object["object_id"],
                            resource_unixtime=resource_time)

        elif event.type == VkBotEventType.WALL_REPOST:
            post_id = event.object["copy_history"][0]["id"]
            self._add_point(user_id=event.object["owner_id"],
                            event=UpdateRatingEvents.ADD_REPOSTED_POST,
                            resource=post_id,
                            resource_unixtime=VkTools.get_post_time(group_id=self._group_id, post_id=post_id))

        if event.type == VkBotEventType.WALL_POST_NEW:
            self._add_point(user_id=event.object.get("signer_id", -1),
                            event=UpdateRatingEvents.ADD_RELEASED_POST,
                            resource=event.object["id"],
                            resource_unixtime=event.object["date"])

        if event.type == VkBotEventType.GROUP_JOIN:
            self.update_last_subs()
            return

    def _update_ratings(self):
        for interval, rating_info_list in self._rating_info.items():
            if self._is_reset_rating(interval):
                self._reset_rating(interval)
                continue

            for rating_info in rating_info_list:
                self._update_rating(interval, rating_info)

    def _reset_rating(self, interval: Interval):
        rating_info_list = self._rating_info.get(interval)
        new_interval = TimeTools.get_period_interval(period=rating_info_list[0].period)
        self._rating_info[new_interval] = rating_info_list
        self._ratings[new_interval] = RatingMembers()
        self._ratings.pop(interval)
        self._rating_info.pop(interval)
        logger.info("reset_rating")

    def _update_rating(self, interval: Interval, rating_info: RatingInfo):
        rating_info.points.clear()
        for member_info in self._ratings[interval].get_all():
            rating_info.points[member_info.member_id] = self._calc_points(point_formula=rating_info.point_formula,
                                                                          member_info=member_info)

    def _calc_points(self, member_info: MemberInfo, point_formula: str) -> EasyMemberInfo:
        res = member_info.get_easy_info()
        res.points = int(TextCalculator(self._formatter_function).get_format_text(text=point_formula,
                                                                              member_info=member_info))

        return res

    def add_rating(self, rating_info: RatingInfo):
        interval = TimeTools.get_period_interval(rating_info.period)
        if interval not in self._ratings:
            self._ratings[interval] = RatingMembers()
            self._rating_info[interval] = [rating_info]
        else:
            self._rating_info[interval].append(rating_info)
        self._init_rating(interval)
        self._update_rating(interval, rating_info)

    def _init_rating(self, interval: Interval):
        logger.info("Инициализируется рейтинг...")
        posts = VkTools.get_posts_from_date(group_id=self._group_id, from_date_unixtime=interval.fr)

        for p in posts:
            logger.debug(f"Сбор информации о посте {p['id']}...")
            likes = VkTools.get_post_liker_ids(group_id=self._group_id, post_id=p["id"],
                                               likes_count=p["likes"]["count"])
            comments = VkTools.get_post_comments(group_id=self._group_id, post_id=p["id"],
                                                 comments_count=p["comments"]["count"])
            reposts = VkTools.get_post_reposts(group_id=self._group_id, post_id=p["id"],
                                               reposts_count=p["reposts"]["count"])

            for i in likes:
                self._add_point(user_id=i, event=UpdateRatingEvents.ADD_LIKED_POST, resource=p['id'],
                                resource_unixtime=p['date'])

            for i in comments:
                self._add_point(user_id=i["from_id"], event=UpdateRatingEvents.ADD_COMMENTED_POST, resource=p['id'],
                                resource_unixtime=p['date'])

            for i in reposts:
                self._add_point(user_id=i["owner_id"], event=UpdateRatingEvents.ADD_REPOSTED_POST, resource=p['id'],
                                resource_unixtime=p['date'])

            self._add_point(user_id=p.get("signer_id", -1), event=UpdateRatingEvents.ADD_RELEASED_POST,
                            resource=p['id'], resource_unixtime=p['date'])

        self.update_donates()

        self.update_last_subs()

        logger.info(f"Инициализация рейтинга завершена.")

    @staticmethod
    def _is_reset_rating(interval: Interval) -> bool:
        return datetime.datetime.now().timestamp() > interval.to

    def _add_point(self, user_id, event: UpdateRatingEvents, resource: int, resource_unixtime: int) -> bool:
        if user_id < 0:
            return True
        for interval, members in self._ratings.items():
            if resource_unixtime < interval.fr or resource_unixtime > interval.to:
                continue
            member: MemberInfo = members.get_member(user_id)
            if not member:
                member = members.add(user_id)
            if event == UpdateRatingEvents.ADD_LIKED_POST:
                member.like_posts.append(resource)
            elif event == UpdateRatingEvents.ADD_LIKED_COMMENT:
                member.like_comments.append(resource)
            elif event == UpdateRatingEvents.ADD_DONATE:
                member.donates += resource
            elif event == UpdateRatingEvents.ADD_RELEASED_POST:
                member.released_posts.append(resource)
            elif event == UpdateRatingEvents.ADD_REPOSTED_POST:
                member.repost_posts.append(resource)
            elif event == UpdateRatingEvents.ADD_COMMENTED_COMMENT:
                member.comment_comments.append(resource)
            elif event == UpdateRatingEvents.ADD_COMMENTED_POST:
                member.comment_posts.append(resource)
            elif event == UpdateRatingEvents.DEL_LIKED_POST:
                member.like_posts.remove(resource)
            elif event == UpdateRatingEvents.DEL_LIKED_COMMENT:
                member.like_comments.remove(resource)
            logger.debug(f"Пользователю {user_id} добавлен ресурс {resource} для {event.name}")
        return True

    @logger.catch(reraise=False)
    def update_donates(self):
        """
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
                self._add_point(d["uid"], "donates", d["sum"])
        """
        pass

    def update_last_subs(self):
        member_ids = VkTools.get_group_member_ids(group_id=self._group_id,
                                                  sort="time_desc",
                                                  count=self._max_last_subs)
        logger.debug(f"Обновлён рейтинг последних подписчиков: {member_ids}")
        for i in range(len(member_ids)):
            self._last_subscriber_ids[i] = member_ids[i]

    def get_last_subscriber_ids(self, number: int) -> typing.List[int]:
        return self._last_subscriber_ids[:number]

    def add_track_last_subscribers(self, max_subs: int):
        self._max_last_subs = max(self._max_last_subs, max_subs)

    @staticmethod
    def get_formula_member_info(member_info: MemberInfo) -> typing.Dict[str, any]:
        return {
            "post_likes": len(member_info.like_posts),
            "post_comments": len(member_info.comment_posts),
            "reposts": len(member_info.repost_posts),
            "posts": len(member_info.released_posts),
            "donates": member_info.donates
        }
