class VkResource:
    def __init__(self, resource_id: int):
        self.resource_id = resource_id


class ResourcePost(VkResource):
    def __init__(self, post_id: int, likes: int = 0, comments: int = 0):
        super().__init__(post_id)
        self.likes = likes
        self.comments = comments


class ResourceRepost(VkResource):
    def __init__(self, repost_id: int, user_id: int, post_id: int, likes: int = 0, views: int = 0):
        super().__init__(repost_id)
        self.post_id = post_id
        self.user_id = user_id
        self.likes = likes
        self.views = views


class ResourceComment(VkResource):
    def __init__(self, comment_id: int, object_id: int, likes: int = 0):
        super().__init__(comment_id)
        self.object_id = object_id
        self.likes = likes
