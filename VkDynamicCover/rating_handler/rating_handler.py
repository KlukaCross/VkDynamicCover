import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
from vk_api.bot_longpoll import VkBotEventType

from VkDynamicCover.text_formatting import TextCalculator, FormatterFunction
from VkDynamicCover.listeners import Subscriber
import typing

from VkDynamicCover.types.interval import Interval
from VkDynamicCover.rating_handler.member_info import MemberInfo
from VkDynamicCover.rating_handler.rating_info import RatingInfo
from VkDynamicCover.types import UpdateRatingEvents, RatingEvent, RatingEventRepost, RatingEventComment, \
    RatingEventLike, RatingEventPost
from VkDynamicCover.utils import VkTools, TimeTools
from VkDynamicCover.types import MemberInfoTypes

RATING_UPDATE_SECONDS = 60
REPOSTS_INFO_UPDATE_SECONDS = 120


class RatingHandler(Subscriber):
    __HANDLERS__ = {}

    def __new__(cls, group_id, *args, **kwargs):
        if group_id not in cls.__HANDLERS__:
            cls.__HANDLERS__[group_id] = super().__new__(cls)
        return cls.__HANDLERS__[group_id]

    def __init__(self, group_id):
        if hasattr(self, "_group_id"):
            return
        self._group_id = group_id
        self._rating_info: typing.Dict[Interval, typing.List[RatingInfo]] = {}
        self._ratings: typing.Dict[Interval, RatingMembers] = {}
        self._last_subscribers: typing.Dict[int, int] = {}
        self._max_last_subs: int = 0

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            func=self._update_ratings,
            trigger="interval",
            seconds=RATING_UPDATE_SECONDS
        )
        self.scheduler.add_job(
            func=self._update_reposts_info,
            trigger="interval",
            seconds=REPOSTS_INFO_UPDATE_SECONDS
        )
        self.scheduler.start()

    def add_rating(self, rating_info: RatingInfo):
        interval = TimeTools.get_period_interval(rating_info.period)
        if interval not in self._ratings:
            self._ratings[interval] = RatingMembers()
            self._rating_info[interval] = [rating_info]
            self._init_rating(interval)
        else:
            self._rating_info[interval].append(rating_info)
        if rating_info.last_subs:
            self._max_last_subs = max(self._max_last_subs, rating_info.places_count)
            self.update_last_subs()
        self._update_rating(interval, rating_info)

    def update(self, event):
        logger.debug(f"Новое событие {event}")
        resource_event: UpdateRatingEvents = UpdateRatingEvents.NONE
        resource_time = 0
        if event.type == VkBotEventType.WALL_REPLY_NEW:
            user_id = event.object["from_id"]
            resource_event = UpdateRatingEvents.ADD_POST_COMMENT
            event_object = RatingEventComment(unixtime=VkTools.get_post_time(group_id=self._group_id,
                                                                             post_id=event.object["post_id"]),
                                              comment_id=event.object["id"],
                                              object_id=event.object["post_id"])

        elif event.type in ("like_add", "like_remove"):
            if abs(event.object["object_owner_id"]) != self._group_id:  # чужие посты не считаются
                return
            object_type = event.object["object_type"]
            if object_type == "post":
                resource_event = UpdateRatingEvents.ADD_POST_LIKE if event.type == "like_add" else \
                    UpdateRatingEvents.DEL_POST_LIKE
                resource_time = VkTools.get_post_time(group_id=self._group_id, post_id=event.object["object_id"])
            elif object_type == "comment":
                resource_event = UpdateRatingEvents.ADD_COMMENT_LIKE if event.type == "like_add" else \
                    UpdateRatingEvents.DEL_COMMENT_LIKE
                resource_time = VkTools.get_post_time(group_id=self._group_id, post_id=event.object["post_id"])
            event_object = RatingEventLike(unixtime=resource_time,
                                           object_id=event.object["object_id"],
                                           count=1 if resource_event in \
                                                      [UpdateRatingEvents.ADD_POST_LIKE,
                                                       UpdateRatingEvents.ADD_COMMENT_LIKE] else -1)
            user_id = event.object["liker_id"]

        elif event.type == VkBotEventType.WALL_REPOST:
            event_object = RatingEventRepost(unixtime=VkTools.get_post_time(group_id=self._group_id,
                                                                            post_id=event.object["copy_history"][0][
                                                                                "id"]),
                                             repost_id=event.object["id"],
                                             post_id=event.object["copy_history"][0]["id"],
                                             user_id=event.object["owner_id"])
            resource_event = UpdateRatingEvents.ADD_REPOST
            user_id = event.object["owner_id"]

        elif event.type == VkBotEventType.WALL_POST_NEW:
            user_id = event.object.get("signer_id", -1)
            resource_event = UpdateRatingEvents.ADD_POST
            event_object = RatingEventPost(unixtime=event.object["date"], post_id=event.object["id"])

        elif event.type == VkBotEventType.GROUP_JOIN:
            self.update_last_subs()
            return

        else:
            return

        self._add_resource(user_id=user_id, event=resource_event, event_object=event_object)

    @logger.catch(reraise=False)
    def update_donates(self):
        pass

    def update_last_subs(self):
        member_ids = VkTools.get_group_member_ids(group_id=self._group_id,
                                                  sort="time_desc",
                                                  count=self._max_last_subs)
        logger.debug(f"Обновлён рейтинг последних подписчиков: {member_ids}")
        self._last_subscribers.clear()
        for i in range(len(member_ids)):
            self._last_subscribers[member_ids[i]] = len(member_ids) - i
            for interval, members in self._ratings.items():
                member: MemberInfo = members.get_member(member_ids[i])
                if not member:
                    members.add(member_ids[i])

    def _update_ratings(self):
        for interval, rating_info_list in self._rating_info.items():
            if self._is_reset_rating(interval):
                self._reset_rating(interval)
                continue

            for rating_info in rating_info_list:
                self._update_rating(interval, rating_info)

    def _update_reposts_info(self):
        for members in self._ratings.values():
            for member in members:
                for repost in member.reposts.copy():
                    info = VkTools.get_repost(repost.user_id, repost.resource_id)
                    if not info:
                        member.reposts.remove(repost)
                        continue
                    repost.likes = info['likes']['count'] if 'likes' in info else 0
                    repost.views = info['views']['count'] if 'views' in info else 0

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
        for member_info in self._ratings[interval]:
            res: typing.Dict[str, int] = member_info.get_info()
            points = TextCalculator(FormatterFunction(lambda x: x)).get_format_text(rating_info.point_formula, res) if \
                not rating_info.last_subs else self._last_subscribers.get(member_info.member_id, 0)
            res[MemberInfoTypes.POINTS.value] = int(float(points))
            rating_info.points[member_info.member_id] = res

    def _init_rating(self, interval: Interval):
        logger.info("Инициализируется рейтинг...")
        posts = VkTools.get_posts_from_date(group_id=self._group_id, from_date_unixtime=interval.fr)

        for p in posts:
            logger.debug(f"Сбор информации о посте {p['id']}...")
            likes = VkTools.get_post_liker_ids(group_id=self._group_id, post_id=p["id"],
                                               likes_count=p["likes"]["count"])
            comments = VkTools.get_post_comments(group_id=self._group_id, post_id=p["id"],
                                                 comments_count=p["comments"]["count"], need_likes=True)
            reposts = VkTools.get_post_reposts(group_id=self._group_id, post_id=p["id"],
                                               reposts_count=p["reposts"]["count"])

            self._add_resource(user_id=p.get("signer_id", -1),
                               event=UpdateRatingEvents.ADD_POST,
                               event_object=RatingEventPost(unixtime=p['date'], post_id=p['id']))

            for i in likes:
                self._add_resource(user_id=i, event=UpdateRatingEvents.ADD_POST_LIKE,
                                   event_object=RatingEventLike(object_id=p['id'], unixtime=p['date'], count=1))

            for i in comments:
                comment_likes = VkTools.get_comment_likes(comment_id=i['id'], owner_id=i['owner_id'])
                likes_count = comment_likes["count"]
                for j in comment_likes['items']:
                    self._add_resource(user_id=j, event=UpdateRatingEvents.ADD_COMMENT_LIKE,
                                       event_object=RatingEventLike(object_id=i['id'], unixtime=p['date'], count=1))
                self._add_resource(user_id=i["from_id"], event=UpdateRatingEvents.ADD_POST_COMMENT,
                                   event_object=RatingEventComment(comment_id=i['id'], object_id=p['id'],
                                                                   likes=likes_count,
                                                                   unixtime=p['date']))

            for i in reposts:
                likes_count = i['likes']['count'] if 'likes' in i else 0
                views_count = i['views']['count'] if 'views' in i else 0
                self._add_resource(user_id=i["owner_id"], event=UpdateRatingEvents.ADD_REPOST,
                                   event_object=RatingEventRepost(repost_id=i['id'], post_id=p['id'], likes=likes_count,
                                                                  views=views_count, unixtime=p['date'],
                                                                  user_id=i["owner_id"]))

        # self.update_donates()

        self.update_last_subs()

        logger.info(f"Инициализация рейтинга завершена.")

    @staticmethod
    def _is_reset_rating(interval: Interval) -> bool:
        return datetime.datetime.now().timestamp() > interval.to

    def _add_resource(self, user_id: int, event: UpdateRatingEvents, event_object) -> bool:
        if user_id < 0:
            return True
        for interval, members in self._ratings.items():
            if event_object.unixtime < interval.fr or event_object.unixtime > interval.to:
                continue
            member: MemberInfo = members.get_member(user_id)
            if not member:
                members.add(user_id)
            members.add_resource(user_id, event, event_object)
            logger.debug(f"Пользователю {user_id} добавлен ресурс для {event.name}")
        return True


class RatingMembers:
    def __init__(self):
        self._rating: typing.Dict[int, MemberInfo] = {}

    def add(self, member_id: int) -> MemberInfo:
        if member_id in self._rating:
            return self._rating[member_id]
        member_info = MemberInfo(member_id=member_id)
        self._rating[member_id] = member_info
        return member_info

    def get_member(self, member_id: int) -> MemberInfo or None:
        return self._rating.get(member_id)

    def get_all(self) -> typing.List[MemberInfo]:
        return list(self._rating.values())

    def add_resource(self, user_id: int, event: UpdateRatingEvents, event_object):
        member = self.get_member(user_id)
        if event == UpdateRatingEvents.ADD_POST_LIKE:
            member.add(MemberInfoTypes.POST_LIKES, event_object)
            self._add_post_like(event_object)
        elif event == UpdateRatingEvents.ADD_COMMENT_LIKE:
            member.add(MemberInfoTypes.COMMENT_LIKES, event_object)
            self._add_comment_like(event_object)
        elif event == UpdateRatingEvents.ADD_DONATE:
            member.add(MemberInfoTypes.DONATES, event_object)
        elif event == UpdateRatingEvents.ADD_POST:
            member.add(MemberInfoTypes.POSTS, event_object)
        elif event == UpdateRatingEvents.ADD_REPOST:
            member.add(MemberInfoTypes.REPOSTS, event_object)
        # elif event == UpdateRatingEvents.ADD_COMMENT_COMMENT:
        #     member.add(MemberInfoTypes.COMMENT_COMMENTS, event_object)
        elif event == UpdateRatingEvents.ADD_POST_COMMENT:
            member.add(MemberInfoTypes.POST_COMMENTS, event_object)
            self._add_post_comment(event_object)
        elif event == UpdateRatingEvents.DEL_POST_LIKE:
            member.remove(MemberInfoTypes.POST_LIKES, event_object)
            self._add_post_like(event_object)
        elif event == UpdateRatingEvents.DEL_COMMENT_LIKE:
            member.remove(MemberInfoTypes.POST_COMMENTS, event_object)
            self._add_comment_like(event_object)

    def __iter__(self):
        return self._rating.values().__iter__()

    def _add_post_like(self, event_object: RatingEventLike):
        for m in self._rating.values():
            pst = m.get_post(event_object.object_id)
            if pst:
                pst.likes += event_object.count
                break

    def _add_comment_like(self, event_object: RatingEventLike):
        for m in self._rating.values():
            pst = m.get_comment(event_object.object_id)
            if pst:
                pst.likes += event_object.count
                break

    def _add_post_comment(self, event_object: RatingEventComment):
        for m in self._rating.values():
            pst = m.get_post(event_object.object_id)
            if pst:
                pst.comments += 1
                break
