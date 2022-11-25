from VkDynamicCover.builders.picture_builder import PictureBuilder
from VkDynamicCover.widgets.profile import Profile, UserInfo

from VkDynamicCover.builders.widget_builder import WidgetBuilder


class ProfileBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Profile:
        kwargs["info"] = UserInfo(**kwargs.get("info", {}))
        kwargs["avatar"] = PictureBuilder().create(**kwargs.get("avatar", {}))

        profile = Profile(**kwargs)
        return profile
