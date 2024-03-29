import datetime

from VkDynamicCover.plugins.scheduler import Scheduler
from loguru import logger
from vk_api.bot_longpoll import VkBotEventType

from VkDynamicCover.text_formatting import TextCalculator, FormatterFunction
from VkDynamicCover.listeners import Subscriber
import typing

from VkDynamicCover.types.interval import Interval
from VkDynamicCover.types.rating_unit_info import RatingUnitInfo
from VkDynamicCover.types import UpdateRatingEvents, RatingEventRepost, RatingEventComment, \
    RatingEventLike, RatingEventPost, RatingEvent
from VkDynamicCover.utils import VkTools, TimeTools
from VkDynamicCover.types import MemberInfoTypes, ResourcePost, ResourceRepost, ResourceComment

RATING_UPDATE_SECONDS = 60
REPOSTS_INFO_UPDATE_SECONDS = 600


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
        self._rating_info: typing.Dict[Interval, typing.List[RatingUnitInfo]] = {}
        self._ratings: typing.Dict[Interval, RatingMembers] = {}
        self._last_subscribers: typing.Dict[int, int] = {}
        self._max_last_subs: int = 0
        Scheduler.add_job(self._update_ratings, trigger="interval", seconds=RATING_UPDATE_SECONDS)
        Scheduler.add_job(self._update_reposts_info, trigger="interval", seconds=REPOSTS_INFO_UPDATE_SECONDS)

    def add_rating(self, rating_info: RatingUnitInfo):
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
        if event.type == VkBotEventType.WALL_REPLY_NEW:
            user_id = event.object["from_id"]
            resource_event = UpdateRatingEvents.ADD_POST_COMMENT
            resource_time = VkTools.get_post_time(group_id=self._group_id, post_id=event.object["post_id"])
            if resource_time is None:
                logger.warning(f"not found time for post {self._group_id}_{event.object['post_id']}")
                return
            event_object = RatingEventComment(unixtime=resource_time,
                                              comment_id=event.object["id"],
                                              object_id=event.object["post_id"])

        elif event.type in ("like_add", "like_remove"):
            if abs(event.object["object_owner_id"]) != self._group_id:  # чужие посты не считаются
                return
            object_type = event.object["object_type"]
            if object_type == "post":
                resource_event = UpdateRatingEvents.ADD_POST_LIKE if event.type == "like_add" else \
                    UpdateRatingEvents.DEL_POST_LIKE
                post_id = event.object["object_id"]
            elif object_type == "comment":
                resource_event = UpdateRatingEvents.ADD_COMMENT_LIKE if event.type == "like_add" else \
                    UpdateRatingEvents.DEL_COMMENT_LIKE
                post_id = event.object["post_id"]
            else:
                return
            resource_time = VkTools.get_post_time(group_id=self._group_id, post_id=post_id)
            if resource_time is None:
                logger.warning(f"not found time for post {self._group_id}_{post_id}")
                return
            event_object = RatingEventLike(unixtime=resource_time,
                                           object_id=event.object["object_id"],
                                           count=1 if resource_event in \
                                                      [UpdateRatingEvents.ADD_POST_LIKE,
                                                       UpdateRatingEvents.ADD_COMMENT_LIKE] else -1)
            user_id = event.object["liker_id"]

        elif event.type == VkBotEventType.WALL_REPOST:
            post_id = event.object["copy_history"][0]["id"]
            resource_time = VkTools.get_post_time(group_id=self._group_id,
                                                  post_id=post_id)
            if resource_time is None:
                logger.warning(f"not found time for repost {self._group_id}_{post_id}")
                return
            event_object = RatingEventRepost(unixtime=resource_time,
                                             repost_id=event.object["id"],
                                             post_id=event.object["copy_history"][0]["id"],
                                             user_id=event.object["owner_id"])
            resource_event = UpdateRatingEvents.ADD_REPOST
            user_id = event.object["owner_id"]

        elif event.type == VkBotEventType.WALL_POST_NEW and event.object["post_type"] not in ["postpone", "suggest"]:
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
            for member in list(members.values()).copy():
                for repost in member.reposts.copy():
                    info: dict = VkTools.get_repost(repost.user_id, repost.resource_id)
                    if info is None:
                        return
                    if not len(info):
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

    def _update_rating(self, interval: Interval, rating_info: RatingUnitInfo):
        rating_info.points.clear()
        for member_info in list(self._ratings[interval].values()).copy():
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
                if "deleted" in i:
                    continue
                comment_likes = VkTools.get_comment_likes(comment_id=i['id'], owner_id=i['owner_id'])
                self._add_resource(user_id=i["from_id"], event=UpdateRatingEvents.ADD_POST_COMMENT,
                                   event_object=RatingEventComment(comment_id=i['id'], object_id=p['id'],
                                                                   likes=0,
                                                                   unixtime=p['date']))
                for j in comment_likes['items']:
                    self._add_resource(user_id=j, event=UpdateRatingEvents.ADD_COMMENT_LIKE,
                                       event_object=RatingEventLike(object_id=i['id'], unixtime=p['date'], count=1))

            for i in reposts:
                likes_count = i['likes']['count'] if 'likes' in i else 0
                views_count = i['views']['count'] if 'views' in i else 0
                self._add_resource(user_id=i["owner_id"], event=UpdateRatingEvents.ADD_REPOST,
                                   event_object=RatingEventRepost(repost_id=i['id'], post_id=p['id'], likes=likes_count,
                                                                  views=views_count, unixtime=p['date'],
                                                                  user_id=i["owner_id"]))

        self.update_last_subs()

        logger.info(f"Инициализация рейтинга завершена.")

    @staticmethod
    def _is_reset_rating(interval: Interval) -> bool:
        return datetime.datetime.now().timestamp() > interval.to

    def _add_resource(self, user_id: int, event: UpdateRatingEvents, event_object: RatingEvent) -> bool:
        if user_id < 0:
            return True
        for interval, members in self._ratings.items():
            if event_object.unixtime < interval.fr or event_object.unixtime > interval.to:
                continue
            member: MemberInfo = members.get_member(user_id)
            if not member:
                members.add(user_id)
            members.add_resource(user_id, event, event_object)
        return True


class RatingMembers:
    def __init__(self):
        self._rating: typing.Dict[int, MemberInfo] = {}

    def add(self, member_id: int) -> "MemberInfo":
        if member_id in self._rating:
            return self._rating[member_id]
        member_info = MemberInfo(member_id=member_id)
        self._rating[member_id] = member_info
        return member_info

    def get_member(self, member_id: int) -> "MemberInfo" or None:
        return self._rating.get(member_id)

    def get_all(self) -> typing.List["MemberInfo"]:
        return list(self._rating.values())

    def add_resource(self, user_id: int, event: UpdateRatingEvents, event_object: RatingEvent):
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
        elif event == UpdateRatingEvents.ADD_POST_COMMENT:
            member.add(MemberInfoTypes.POST_COMMENTS, event_object)
            self._add_post_comment(event_object)
        elif event == UpdateRatingEvents.DEL_POST_LIKE:
            member.remove(MemberInfoTypes.POST_LIKES, event_object)
            self._add_post_like(event_object)
        elif event == UpdateRatingEvents.DEL_COMMENT_LIKE:
            member.remove(MemberInfoTypes.COMMENT_LIKES, event_object)
            self._add_comment_like(event_object)

    def __iter__(self):
        return self._rating.values().__iter__()

    def values(self):
        return self._rating.values()

    def _add_post_like(self, event_object: RatingEventLike):
        for m in self._rating.values():
            pst = m.get_post(event_object.object_id)
            if pst:
                pst.likes += event_object.count
                break

    def _add_comment_like(self, event_object: RatingEventLike):
        for m in self._rating.values():
            cmt = m.get_comment(event_object.object_id)
            if cmt:
                cmt.likes += event_object.count
                break

    def _add_post_comment(self, event_object: RatingEventComment):
        for m in self._rating.values():
            pst = m.get_post(event_object.object_id)
            if pst:
                pst.comments += 1
                break


class MemberInfo:
    def __init__(self, member_id: int):
        self._member_id = member_id

        self._post_likes: int = 0
        self._comment_likes: int = 0
        self._post_comments: typing.List[ResourceComment] = []
        self._reposts: typing.List[ResourceRepost] = []
        self._released_posts: typing.List[ResourcePost] = []
        self._donates: int = 0

    @property
    def member_id(self) -> int:
        return self._member_id

    @property
    def reposts(self) -> typing.List[ResourceRepost]:
        return self._reposts

    def get_info(self) -> typing.Dict[str, int]:
        views_of_reposts = 0
        likes_of_reposts = 0
        for i in self.reposts:
            views_of_reposts += i.views
            likes_of_reposts += i.likes

        likes_of_comments = 0
        for i in self._post_comments:
            likes_of_comments += i.likes

        likes_of_posts = 0
        comments_of_posts = 0
        for i in self._released_posts:
            likes_of_posts += i.likes
            comments_of_posts += i.comments

        res = {MemberInfoTypes.MEMBER_INFO.value: self._member_id,
               MemberInfoTypes.COMMENT_LIKES.value: self._comment_likes,
               MemberInfoTypes.POST_LIKES.value: self._post_likes,
               MemberInfoTypes.POST_COMMENTS.value: len(self._post_comments),
               MemberInfoTypes.REPOSTS.value: len(self._reposts),
               MemberInfoTypes.POSTS.value: len(self._released_posts),
               MemberInfoTypes.DONATES.value: self._donates,
               MemberInfoTypes.VIEWS_OF_REPOSTS.value: views_of_reposts,
               MemberInfoTypes.LIKES_OF_REPOSTS.value: likes_of_reposts,
               MemberInfoTypes.LIKES_OF_COMMENTS.value: likes_of_comments,
               MemberInfoTypes.LIKES_OF_POSTS.value: likes_of_posts,
               MemberInfoTypes.COMMENTS_OF_POSTS.value: comments_of_posts}
        return res

    def add(self, tp: MemberInfoTypes, event_object):
        if tp == MemberInfoTypes.POST_LIKES:
            self._post_likes += event_object.count
        elif tp == MemberInfoTypes.COMMENT_LIKES:
            self._comment_likes += event_object.count
        elif tp == MemberInfoTypes.POST_COMMENTS:
            self._post_comments.append(ResourceComment(comment_id=event_object.comment_id,
                                                       object_id=event_object.object_id,
                                                       likes=event_object.likes))
        elif tp == MemberInfoTypes.REPOSTS:
            self._reposts.append(ResourceRepost(repost_id=event_object.repost_id,
                                                user_id=event_object.user_id,
                                                post_id=event_object.post_id,
                                                likes=event_object.likes,
                                                views=event_object.views))
        elif tp == MemberInfoTypes.POSTS:
            self._released_posts.append(ResourcePost(post_id=event_object.post_id))
        elif tp == MemberInfoTypes.DONATES:
            self._donates -= event_object.count

    def remove(self, tp: MemberInfoTypes, event_object: RatingEvent):
        if tp == MemberInfoTypes.POST_LIKES:
            self._post_likes -= 1
        elif tp == MemberInfoTypes.COMMENT_LIKES:
            self._comment_likes -= 1
        elif tp == MemberInfoTypes.POST_COMMENTS:
            for a in self._post_comments:
                if a.resource_id == event_object.post_id:
                    self._post_comments.remove(a)
                    break
        elif tp == MemberInfoTypes.REPOSTS:
            for a in self._reposts:
                if a.resource_id == event_object.repost_id:
                    self._reposts.remove(a)
                    break
        elif tp == MemberInfoTypes.POSTS:
            for a in self._released_posts:
                if a.resource_id == event_object.post_id:
                    self._released_posts.remove(a)
                    break
        elif tp == MemberInfoTypes.DONATES:
            self._donates -= event_object.count

    def get_post(self, post_id: int) -> typing.Union[None, ResourcePost]:
        for a in self._released_posts:
            if a.resource_id == post_id:
                return a
        return None

    def get_repost(self, repost_id: int) -> typing.Union[None, ResourceRepost]:
        for a in self._reposts:
            if a.resource_id == repost_id:
                return a
        return None

    def get_comment(self, post_id: int) -> typing.Union[None, ResourceComment]:
        for a in self._post_comments:
            if a.resource_id == post_id:
                return a
        return None
