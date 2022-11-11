import typing


class MemberInfo:
    def __init__(self, member_id: int):
        self.member_id = member_id

        self.like_posts: typing.List[int] = []
        self.like_comments: typing.List[int] = []
        self.comment_posts: typing.List[int] = []
        self.comment_comments: typing.List[int] = []
        self.repost_posts: typing.List[int] = []
        self.released_posts: typing.List[int] = []
        self.donates: int = 0
