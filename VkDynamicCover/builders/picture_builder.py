from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.widgets.picture import Picture, RandomPicture, RandomLocalPicture, RandomAlbumPicture, UrlPicture, \
    LocalPicture, VkAvatar


class PictureBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Picture:
        if "type" not in kwargs:
            kwargs["type"] = "Picture"
        if self._is_random_picture(kwargs):
            if self._is_path_picture(kwargs):
                return RandomLocalPicture(**kwargs)
            elif self._is_album_picture(kwargs):
                return RandomAlbumPicture(**kwargs)
        elif self._is_avatar_picture(kwargs):
            return VkAvatar(**kwargs)
        elif self._is_path_picture(kwargs):
            return LocalPicture(**kwargs)
        elif self._is_url_picture(kwargs):
            return UrlPicture(**kwargs)

    def _is_random_picture(self, kwargs) -> bool:
        return kwargs.get("type") == RandomPicture.__name__

    def _is_path_picture(self, kwargs) -> bool:
        return kwargs.get("path") is not None

    def _is_url_picture(self, kwargs) -> bool:
        return kwargs.get("url") is not None

    def _is_album_picture(self, kwargs) -> bool:
        return kwargs.get("album_url") is not None

    def _is_avatar_picture(self, kwargs) -> bool:
        return kwargs.get("type") == VkAvatar.__name__
