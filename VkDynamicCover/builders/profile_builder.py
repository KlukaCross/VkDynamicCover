from VkDynamicCover.builders.picture_builder import PictureBuilder
from VkDynamicCover.widgets.profile import ProfileControl, ProfileDrawer, ProfileInfo, \
    UserInfoControl, UserInfoDrawer, UserInfoInfo
from VkDynamicCover.widgets.widget import WidgetDesigner
from VkDynamicCover.builders.text_builder import TextBuilder

from VkDynamicCover.builders.widget_builder import WidgetBuilder


class ProfileBuilder(WidgetBuilder):
    def create(self, **kwargs) -> ProfileControl:
        kwargs["info"] = UserInfoBuilder().create(**kwargs)
        kwargs["avatar"] = PictureBuilder().create(**kwargs.get("avatar", {}))

        if "type" not in kwargs:
            kwargs["type"] = "Profile"

        drawer = ProfileDrawer()
        designer = WidgetDesigner()
        info = ProfileInfo(**kwargs)
        return ProfileControl(drawer=drawer, designer=designer, info=info)


class UserInfoBuilder(WidgetBuilder):
    def create(self, **kwargs) -> UserInfoControl:
        if "type" not in kwargs:
            kwargs["type"] = "UserInfo"
        kwargs["text"] = TextBuilder().create(**kwargs)

        drawer = UserInfoDrawer()
        designer = WidgetDesigner()
        info = UserInfoInfo(**kwargs)
        return UserInfoControl(drawer=drawer, designer=designer, info=info)
