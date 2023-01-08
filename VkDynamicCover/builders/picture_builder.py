from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.widgets.picture import Picture, RandomLocalPicture, RandomAlbumPicture, UrlPicture, LocalPicture, \
    VkAvatar


class PictureBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Picture:
        if "type" not in kwargs:
            kwargs["type"] = "Picture"
        if "path" in kwargs:
            if "random_function" in kwargs:
                return RandomLocalPicture(**kwargs)
            return LocalPicture(**kwargs)
        if "url" in kwargs:
            if "random_function" in kwargs:
                return RandomAlbumPicture(**kwargs)
            return UrlPicture(**kwargs)
        if "user_id" in kwargs:
            return VkAvatar(**kwargs)
