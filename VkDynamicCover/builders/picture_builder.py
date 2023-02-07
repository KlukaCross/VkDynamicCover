from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.widgets.picture import PictureControl, PictureDrawer, PictureDesigner, PictureInfo, \
    RandomPictureControl, RandomAlbumPictureDesigner, RandomAlbumPictureInfo, RandomLocalPictureDesigner, \
    UrlPictureInfo, UrlPictureDesigner, LocalPictureInfo, LocalPictureDesigner, \
    VkAvatarControl, VkAvatarDesigner, VkAvatarInfo


class PictureBuilder(WidgetBuilder):
    def create(self, **kwargs) -> PictureControl:
        if "type" not in kwargs:
            kwargs["type"] = "Picture"
        control = PictureControl
        drawer = PictureDrawer
        designer = PictureDesigner
        info = PictureInfo
        if self._is_random_picture(kwargs):
            control = RandomPictureControl
            if self._is_path_picture(kwargs):
                designer = RandomLocalPictureDesigner
                info = LocalPictureInfo
            elif self._is_album_picture(kwargs):
                designer = RandomAlbumPictureDesigner
                info = RandomAlbumPictureInfo
        elif self._is_avatar_picture(kwargs):
            designer = VkAvatarDesigner
            info = VkAvatarInfo
            control = VkAvatarControl
        elif self._is_path_picture(kwargs):
            designer = LocalPictureDesigner
            info = LocalPictureInfo
            control = PictureControl
        elif self._is_url_picture(kwargs):
            designer = UrlPictureDesigner
            info = UrlPictureInfo
            control = PictureControl
        return control(drawer=drawer(), designer=designer(), info=info(**kwargs))

    def _is_random_picture(self, kwargs) -> bool:
        return kwargs.get("type") == RandomPictureControl.__TYPE__

    def _is_path_picture(self, kwargs) -> bool:
        return kwargs.get("path") is not None

    def _is_url_picture(self, kwargs) -> bool:
        return kwargs.get("url") is not None

    def _is_album_picture(self, kwargs) -> bool:
        return kwargs.get("album_url") is not None

    def _is_avatar_picture(self, kwargs) -> bool:
        return kwargs.get("type") == VkAvatarControl.__TYPE__
