from VkDynamicCover.builders import PictureBuilder
from VkDynamicCover.builders.text_builder import TextBuilder
from VkDynamicCover.builders.profile_builder import ProfileBuilder
from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.rating_handler.rating_handler import RatingHandler
from VkDynamicCover.listeners import LongpollListener
from VkDynamicCover.rating_handler.rating_info import RatingInfo
from VkDynamicCover.widgets.rating import Rating, RatingPlace

DEFAULT_PERIOD = "month"


class RatingBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Rating:
        places = []
        for place in kwargs.get("places", []):
            places.append(RatingPlaceBuilder().create(**place))

        kwargs["places"] = places
        kwargs["rating_info"] = RatingInfo(period=kwargs.get("period", DEFAULT_PERIOD),
                                           ban_list=kwargs.get("ban_list", []),
                                           point_formula=kwargs.get("point_formula", ""),
                                           places_count=len(kwargs.get("places", [])),
                                           last_subs=True if kwargs.get("last_subs", False) == "true" else False)
        kwargs["Text"] = TextBuilder().create(**kwargs)

        rating = Rating(**kwargs)
        handler = RatingHandler(kwargs["group_id"])
        LongpollListener(kwargs["group_id"]).subscribe(handler)
        handler.add_rating(kwargs["rating_info"])

        return rating


class RatingPlaceBuilder(WidgetBuilder):
    def create(self, **kwargs) -> RatingPlace:
        if "type" not in kwargs:
            kwargs["type"] = "RatingPlace"
        if "default_avatar" in kwargs:
            kwargs["default_avatar"] = PictureBuilder().create(**kwargs["default_avatar"])
        kwargs["profile"] = ProfileBuilder().create(**kwargs)

        return RatingPlace(**kwargs)
