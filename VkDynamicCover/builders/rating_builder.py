from VkDynamicCover.builders.text_builder import TextBuilder
from VkDynamicCover.builders.profile_builder import ProfileBuilder
from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.rating_handler.rating_handler import RatingHandler
from VkDynamicCover.listeners import LongpollListener
from VkDynamicCover.types.rating_info import RatingInfo
from VkDynamicCover.widgets.rating import Rating, RatingPlace


class RatingBuilder(WidgetBuilder):
    def create(self, **kwargs) -> Rating:
        places = []
        for place in kwargs.get("places", []):
            places.append(RatingPlaceBuilder().create(**place))

        kwargs["places"] = places
        kwargs["rating_info"] = RatingInfo(period=kwargs.get("period", "month"),
                                           ban_list=kwargs.get("ban_list", []),
                                           point_formula=kwargs.get("point_formula", ""))
        kwargs["text"] = TextBuilder().create(**kwargs)

        rating = Rating(**kwargs)
        handler = RatingHandler(kwargs["group_id"])
        LongpollListener(kwargs["group_id"]).subscribe(handler)
        handler.add_rating(kwargs["rating_info"])

        return rating


class RatingPlaceBuilder(WidgetBuilder):
    def create(self, **kwargs) -> RatingPlace:
        if "type" not in kwargs:
            kwargs["type"] = "RatingPlace"
        kwargs["profile"] = ProfileBuilder().create(**kwargs)

        return RatingPlace(**kwargs)
