import typing
from functools import reduce

from VkDynamicCover.types import MemberInfoTypes, ResourcePost, ResourceRepost, ResourceComment


class MemberInfo:
    def __init__(self, member_id: int):
        self._member_id = member_id

        self._post_likes: int = 0
        self._comment_likes: int = 0
        self._post_comments: typing.List[ResourceComment] = []
        self._comment_comments: typing.List[ResourceComment] = []
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

    def remove(self, tp: MemberInfoTypes, event_object):
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
