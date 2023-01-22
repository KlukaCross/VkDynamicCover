from enum import Enum


class MemberInfoTypes(Enum):
    MEMBER_INFO = "member_info"
    POINTS = "points"
    POST_LIKES = "post_likes"
    COMMENT_LIKES = "comment_likes"
    POST_COMMENTS = "post_comments"
    REPOSTS = "reposts"
    POSTS = "posts"
    DONATES = "donates"
    # COMMENT_COMMENTS = "comment_comments"

    VIEWS_OF_REPOSTS = "views_of_reposts"
    LIKES_OF_REPOSTS = "likes_of_reposts"
    LIKES_OF_COMMENTS = "likes_of_comments"
    LIKES_OF_POSTS = "likes_of_posts"
    COMMENTS_OF_POSTS = "comments_of_posts"
