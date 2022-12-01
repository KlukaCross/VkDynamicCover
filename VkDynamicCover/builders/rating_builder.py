from VkDynamicCover.builders import TextBuilder
from VkDynamicCover.builders.profile_builder import ProfileBuilder
from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.helpers.rating.rating_handler import RatingHandler
from VkDynamicCover.listeners import LongpollListener
from VkDynamicCover.types.rating_info import RatingInfo
from VkDynamicCover.widgets.rating import Rating, RatingPlace, RatingPlaceInfo


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
        RatingHandlerBuilder().create(group_id=kwargs["group_id"]).add_rating(kwargs["rating_info"])

        return rating


class RatingPlaceBuilder(WidgetBuilder):
    def create(self, **kwargs) -> RatingPlace:
        kwargs["profile"] = ProfileBuilder().create(**kwargs["profile"])
        kwargs["text"] = RatingPlaceInfoBuilder().create(**kwargs["text"])

        return RatingPlace(**kwargs)


class RatingPlaceInfoBuilder(WidgetBuilder):
    def create(self, **kwargs) -> RatingPlaceInfo:
        return RatingPlaceInfo(**kwargs)


class RatingHandlerBuilder:
    def create(self, **kwargs) -> RatingHandler:
        group_id = kwargs["group_id"]
        handler = RatingHandler(group_id)
        LongpollListener(group_id).subscribe(handler)

        return handler
