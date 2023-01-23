import typing


class RatingInfo:
    def __init__(self, period: str, ban_list: list, point_formula: str, places_count: int, last_subs: bool):
        self.period = period
        self.ban_list = ban_list
        self.point_formula = point_formula
        self.places_count = places_count
        self.last_subs = last_subs
        self.points: typing.Dict[int, typing.Dict[str, int]] = {}
