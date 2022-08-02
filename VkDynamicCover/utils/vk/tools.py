import random

from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
import requests

from loguru import logger


def create_session(token) -> vk_api.VkApi:
    return vk_api.VkApi(token=token)


def push_cover(vk_session: vk_api.VkApi, surface_bytes: bytes, surface_width, surface_height, group_id: int):
    vk_meth = vk_session.get_api()
    upload_photo_url = vk_meth.photos.getOwnerCoverPhotoUploadServer(group_id=-group_id,
                                                                crop_x=0, crop_y=0,
                                                                crop_x2=surface_width,
                                                                crop_y2=surface_height)["upload_url"]
    pht = requests.post(upload_photo_url, files={"photo": surface_bytes}).json()
    vk_meth.photos.saveOwnerCoverPhoto(hash=pht["hash"], photo=pht["photo"])


def get_random_picture_url(vk_session: vk_api.VkApi, group_id: str, album_id: str) -> str:
    vk_meth = vk_session.get_api()
    count = vk_meth.photos.get(owner_id=group_id, album_id=album_id, count=1)["count"]
    random_offset = random.randint(0, count-1)
    random_req = vk_meth.photos.get(owner_id=group_id, album_id=album_id, offset=random_offset, count=1)["items"][0]
    photo_url = None
    max_width = 0
    for i in random_req["sizes"]:
        if i["width"] > max_width:
            photo_url = i["url"]
            max_width = i["width"]

    return photo_url


def get_group_info(vk_session: vk_api.VkApi, group_id: int, fields=""):
    vk_meth = vk_session.get_api()
    return vk_meth.groups.getById(group_id=-group_id, fields=fields)[0]


def get_group_statistics(vk_session: vk_api.VkApi, group_id: int, app_id: int,
                         timestamp_from: int = "", timestamp_to: int = "", interval: str = "day",
                         intervals_count: int = 1, extended: bool = False):
    vk_meth = vk_session.get_api()
    req = vk_meth.stats.get(group_id=-group_id, app_id=app_id,
                            timestamp_from=timestamp_from, timestamp_to=timestamp_to,
                            interval=interval, intervals_count=intervals_count, extended=extended)
    return req


def get_post(vk_session: vk_api.VkApi, group_id: int, post_id: int):
    vk_meth = vk_session.get_api()
    return vk_meth.wall.getById(posts=[f"{group_id}_{post_id}"])[0]


def get_posts_from_date(vk_session: vk_api.VkApi, group_id: int, from_date_unixtime: int):
    vk_meth = vk_session.get_api()
    req = vk_meth.wall.get(owner_id=group_id)
    count_posts = req["count"]
    if req["items"][0].get("is_pinned") and req["items"][0]["date"] >= from_date_unixtime:
        yield req["items"][0]

    for i in range(count_posts//100+1):
        req = vk_meth.wall.get(owner_id=group_id, count=100, offset=1+i*100)
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


def get_post_liker_ids(vk_session: vk_api.VkApi, group_id: int, post_id: int, likes_count: int):
    vk_meth = vk_session.get_api()
    for i in range(likes_count//1000+1):
        req = vk_meth.likes.getList(type="post", owner_id=group_id, item_id=post_id,
                                    count=1000, offset=i*1000)
        for v in req["items"]:
            yield v


def get_post_comments(vk_session: vk_api.VkApi, group_id: int, post_id: int, comments_count: int):
    vk_meth = vk_session.get_api()
    for i in range(comments_count//100+1):
        req = vk_meth.wall.getComments(owner_id=group_id, post_id=post_id, offset=i*100, count=100)
        for v in req["items"]:
            yield v


def get_post_reposts(vk_session: vk_api.VkApi, group_id: int, post_id: int, reposts_count: int):
    vk_meth = vk_session.get_api()
    for i in range(reposts_count//100+1):
        req = vk_meth.wall.getReposts(owner_id=group_id, post_id=post_id, offset=i*100, count=100)
        for v in req["items"]:
            yield v


def get_user(vk_session: vk_api.VkApi, user_id: int, fields=""):
    vk_meth = vk_session.get_api()
    return vk_meth.users.get(user_ids=user_id, fields=fields)[0]


def get_comment(vk_session: vk_api.VkApi, group_id: int, comment_id: int):
    vk_meth = vk_session.get_api()
    return vk_meth.wall.getComment(owner_id=group_id, comment_id=comment_id)["items"][0]


@logger.catch(reraise=True)
def longpoll_listener(vk_session: vk_api.VkApi, group_id: int, callback, **kwargs: dict):
    longpoll = VkBotLongPoll(vk_session, group_id=-group_id)
    for event in longpoll.listen():
        callback(event=event, **kwargs)
