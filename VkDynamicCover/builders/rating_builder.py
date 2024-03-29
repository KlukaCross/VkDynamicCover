from VkDynamicCover.builders import PictureBuilder
from VkDynamicCover.builders.text_builder import TextBuilder
from VkDynamicCover.builders.profile_builder import ProfileBuilder
from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.plugins.rating_handler import RatingHandler
from VkDynamicCover.listeners import LongpollListener
from VkDynamicCover.types.rating_unit_info import RatingUnitInfo
from VkDynamicCover.widgets.rating import RatingControl, RatingDrawer, RatingDesigner, RatingInfo, \
    RatingPlaceControl, RatingPlaceDrawer, RatingPlaceDesigner, RatingPlaceInfo

DEFAULT_PERIOD = "month"


class RatingBuilder(WidgetBuilder):
    def create(self, **kwargs) -> RatingControl:
        places = []
        for place in kwargs.get("places", []):
            places.append(RatingPlaceBuilder().create(**place))

        kwargs["places"] = places
        kwargs["rating_info"] = RatingUnitInfo(period=kwargs.get("period", DEFAULT_PERIOD),
                                               ban_list=kwargs.get("ban_list", []),
                                               point_formula=kwargs.get("point_formula", ""),
                                               places_count=len(kwargs.get("places", [])),
                                               last_subs=True if kwargs.get("last_subs", False) == "true" else False)
        kwargs["text"] = TextBuilder().create(**kwargs)

        handler = RatingHandler(kwargs["group_id"])
        LongpollListener(kwargs["group_id"]).subscribe(handler)
        handler.add_rating(kwargs["rating_info"])

        drawer = RatingDrawer()
        designer = RatingDesigner()
        info = RatingInfo(**kwargs)

        return RatingControl(drawer=drawer, designer=designer, info=info)


class RatingPlaceBuilder(WidgetBuilder):
    def create(self, **kwargs) -> RatingPlaceControl:
        if "type" not in kwargs:
            kwargs["type"] = "RatingPlace"
        if "default_avatar" in kwargs:
            kwargs["default_avatar"] = PictureBuilder().create(**kwargs["default_avatar"])
        kwargs["profile"] = ProfileBuilder().create(**kwargs)

        drawer = RatingPlaceDrawer()
        designer = RatingPlaceDesigner()
        info = RatingPlaceInfo(**kwargs)

        return RatingPlaceControl(drawer=drawer, designer=designer, info=info)
