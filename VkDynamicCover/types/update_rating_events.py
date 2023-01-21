from enum import Enum


class UpdateRatingEvents(Enum):
    NONE = -1
    ADD_POST_LIKE = 0
    ADD_COMMENT_LIKE = 1
    ADD_POST_COMMENT = 2
    ADD_COMMENT_COMMENT = 3
    ADD_REPOST = 4
    ADD_POST = 5
    ADD_DONATE = 6

    DEL_POST_LIKE = 7
    DEL_COMMENT_LIKE = 8


class RatingEvent:
    def __init__(self, unixtime):
        self.unixtime = unixtime


class RatingEventLike(RatingEvent):
    def __init__(self, unixtime, object_id, count):
        super().__init__(unixtime)
        self.object_id = object_id
        self.count = count


class RatingEventComment(RatingEvent):
    def __init__(self, unixtime, comment_id, object_id, likes):
        super().__init__(unixtime)
        self.comment_id = comment_id
        self.object_id = object_id
        self.likes = likes


class RatingEventPost(RatingEvent):
    def __init__(self, unixtime, post_id):
        super().__init__(unixtime)
        self.post_id = post_id


class RatingEventRepost(RatingEvent):
    def __init__(self, unixtime, repost_id, post_id, user_id, likes=0, views=0):
        super().__init__(unixtime)
        self.repost_id = repost_id
        self.post_id = post_id
        self.user_id = user_id
        self.likes = likes
        self.views = views

