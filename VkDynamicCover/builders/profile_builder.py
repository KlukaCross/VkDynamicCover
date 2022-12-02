from VkDynamicCover.builders.picture_builder import PictureBuilder
from VkDynamicCover.widgets.profile import Profile, UserInfo

from VkDynamicCover.builders.widget_builder import WidgetBuilder


class ProfileBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Profile:
        kwargs["info"] = UserInfoBuilder().create(**kwargs)
        kwargs["avatar"] = PictureBuilder().create(**kwargs.get("avatar", {}))

        if "type" not in kwargs:
            kwargs["type"] = "Profile"
        profile = Profile(**kwargs)
        return profile


class UserInfoBuilder(WidgetBuilder):
    def create(self, **kwargs) -> UserInfo:
        if "type" not in kwargs:
            kwargs["type"] = "UserInfo"
        return UserInfo(**kwargs)