import typing


class RatingInfo:
    def __init__(self, period: str, ban_list: list, point_formula: str):
        self.period = period
        self.ban_list = ban_list
        self.point_formula = point_formula
        self.points: typing.Dict[int, typing.Dict[str, int]] = {}
