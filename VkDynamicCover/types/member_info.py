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

    def get_easy_info(self) -> "EasyMemberInfo":
        res = EasyMemberInfo()
        res.member_id = self.member_id
        res.post_likes = len(self.like_posts)
        res.comment_likes = len(self.like_comments)
        res.post_comments = len(self.comment_posts)
        res.reposts = len(self.repost_posts)
        res.posts = len(self.released_posts)
        res.donates = self.donates
        return res


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
