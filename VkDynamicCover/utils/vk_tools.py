import io
import typing

from VkDynamicCover.types import MetaSingleton
import requests
from vk_api import vk_api, exceptions, upload
from vk_api.bot_longpoll import VkBotLongPoll
import time

from loguru import logger


API_CODE_INVALID_PHOTO = 129
API_CODE_INTERNAL_ERROR = 10
API_CODE_RATE_LIMIT_REACHED = 29

RETRY_SLEEP_SECONDS = 10
RETRY_COUNT = 3


def api_retry(func):
    def wrapper(*args, **kwargs):
        error_callback = kwargs.get("error_callback", lambda e: logger.error(e))
        c = RETRY_COUNT
        last_error = None
        while c > 0:
            try:
                return func(*args, **kwargs)
            except exceptions.ApiError as e:
                last_error = e
                if e.code not in [API_CODE_INVALID_PHOTO, API_CODE_INTERNAL_ERROR, API_CODE_RATE_LIMIT_REACHED]:
                    break
            except (requests.RequestException, exceptions.VkApiError, exceptions.ApiHttpError) as e:
                last_error = e

            time.sleep(RETRY_SLEEP_SECONDS)
            c -= 1

        error_callback(last_error)

    return wrapper


class _VkTools(metaclass=MetaSingleton):
    def __init__(self):
        self._vk_session = None
        self._app_id = None
        self._vk_meth = None
        self._vk_upload = None

    def init(self, vk_session: vk_api.VkApi, app_id: str):
        self._vk_session = vk_session
        self._app_id = app_id
        self._vk_meth = self._vk_session.get_api()
        self._vk_upload = upload.VkUpload(self._vk_session)

    @staticmethod
    def create_session(token) -> vk_api.VkApi:
        return vk_api.VkApi(token=token)

    @api_retry
    def push_cover(self, surface_bytes: io.BytesIO, surface_width: int, surface_height: int, group_id: int):
        self._vk_upload.photo_cover(photo=surface_bytes, group_id=group_id, crop_x=0, crop_y=0,
                                    crop_x2=surface_width, crop_y2=surface_height)

    @api_retry
    def get_random_image_from_album(self, group_id: int, album_id: str, rand_func: typing.Callable[[int, dict], int],
                                    **kwargs) -> str or None:
        count = self._vk_meth.photos.get(owner_id=-group_id, album_id=album_id, count=1).get("count", 0)
        random_offset = rand_func(count, **kwargs)
        random_req = \
            self._vk_meth.photos.get(owner_id=-group_id, album_id=album_id, offset=random_offset, count=1).get("items")
        if random_req is None:
            return None
        photo_url = None
        max_width = 0
        for i in random_req[0]["sizes"]:
            if i["width"] > max_width:
                photo_url = i["url"]
                max_width = i["width"]

        return photo_url

    @api_retry
    def get_group_info(self, group_id: int, fields="") -> dict:
        groups = self._vk_meth.groups.getById(group_id=group_id, fields=fields)
        return groups[0] if groups is not None and len(groups) > 0 else {}

    @api_retry
    def get_group_statistics(self, group_id: int, timestamp_from: int = "", timestamp_to: int = "",
                             interval: str = "day", intervals_count: int = 1, extended: bool = False) -> list:
        req = self._vk_meth.stats.get(group_id=group_id, app_id=self._app_id,
                                      timestamp_from=timestamp_from, timestamp_to=timestamp_to,
                                      interval=interval, intervals_count=intervals_count, extended=extended)
        return req if req is not None else []

    @api_retry
    def get_group_post(self, group_id: int, post_id: int) -> dict:
        posts = self._vk_meth.wall.getById(posts=[f"-{group_id}_{post_id}"])
        return posts[0] if posts and len(posts) else {}

    @api_retry
    def get_user_post(self, user_id: int, post_id: int) -> dict:
        posts = self._vk_meth.wall.getById(posts=[f"{user_id}_{post_id}"])
        if posts and len(posts):
            return posts[0]
        return {}

    @api_retry
    def get_repost(self, user_id: int, repost_id: int) -> dict:
        post = self.get_user_post(user_id, repost_id)
        return post if post else {}

    @api_retry
    def get_post_time(self, group_id: int, post_id: int) -> int or None:
        post = self.get_group_post(group_id, post_id)
        return post.get("date") if post else None

    @api_retry
    def get_posts_from_date(self, group_id: int, from_date_unixtime: int) -> list:
        req = self._vk_meth.wall.get(owner_id=-group_id)
        if req is None:
            return
        count_posts = req["count"]
        start_i = 0
        # is maybe pinned post
        if req["items"][0]["date"] >= from_date_unixtime:
            start_i += 1
            yield req["items"][0]

        for i in range(count_posts // 100 + 1):
            req = self._vk_meth.wall.get(owner_id=-group_id, count=100, offset=start_i + i * 100)
            if req["items"][-1]["date"] < from_date_unixtime:
                break
            for p in req["items"]:
                yield p
        else:
            return

        for post in req["items"]:
            if post["date"] >= from_date_unixtime:
                yield post
            else:
                return

    @api_retry
    def get_post_liker_ids(self, group_id: int, post_id: int, likes_count: int) -> list:
        for i in range(likes_count // 1000 + 1):
            req = self._vk_meth.likes.getList(type="post", owner_id=-group_id, item_id=post_id,
                                              count=1000, offset=i * 1000)
            if req is None:
                return
            for v in req["items"]:
                yield v

    @api_retry
    def get_comment_likes(self, comment_id: int, owner_id: int) -> list:
        res = self._vk_meth.likes.getList(type="comment", owner_id=owner_id, item_id=comment_id)
        if res is None:
            return []
        return res

    @api_retry
    def get_post_comments(self, group_id: int, post_id: int, comments_count: int, need_likes=False) -> list:
        """ возвращает все комментарии под постом, включая комментарии в ветках"""
        vk_meth = self._vk_session.get_api()
        for i in range(comments_count // 100 + 1):
            req = vk_meth.wall.getComments(owner_id=-group_id, post_id=post_id, offset=i * 100, count=100,
                                           thread_items_count=10, need_likes=need_likes)
            if req is None:
                return
            for v in req["items"]:
                thread_count = v["thread"]["count"]
                if thread_count > 10:
                    for j in range(thread_count // 100 + 1):
                        reqq = vk_meth.wall.getComments(owner_id=-group_id, post_id=post_id, offset=j * 100, count=100,
                                                        need_likes=need_likes)
                        for vv in reqq["items"]:
                            yield vv
                else:
                    for vv in v["thread"]["items"]:
                        yield vv
                yield v

    @api_retry
    def get_post_reposts(self, group_id: int, post_id: int, reposts_count: int) -> list:
        vk_meth = self._vk_session.get_api()
        for i in range(reposts_count // 100 + 1):
            req = vk_meth.wall.getReposts(owner_id=-group_id, post_id=post_id, offset=i * 100, count=100)
            if req is None:
                return
            for v in req["items"]:
                yield v

    @api_retry
    def get_user(self, user_id: int, fields="") -> dict:
        users = self._vk_meth.users.get(user_ids=user_id, fields=fields)
        return users[0] if users and len(users) else {}

    @api_retry
    def get_comment(self, group_id: int, comment_id: int) -> dict:
        comments = self._vk_meth.wall.getComment(owner_id=-group_id, comment_id=comment_id)
        return comments["items"][0] if comments else {}

    @api_retry
    def get_group_member_ids(self, group_id: int, sort, count=10) -> list:
        members = self._vk_meth.groups.getMembers(group_id=group_id, sort=sort, count=count)
        return members["items"] if members else []

    @api_retry
    def get_longpoll(self, group_id: int) -> VkBotLongPoll:
        return VkBotLongPoll(self._vk_session, group_id=group_id)


VkTools = _VkTools()
