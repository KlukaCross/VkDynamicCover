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


class EasyMemberInfo:
    def __init__(self):
        self.member_id = 0

        self.points = 0
        self.post_likes = 0
        self.comment_likes = 0
        self.post_comments = 0
        self.reposts = 0
        self.posts = 0
        self.donates = 0
