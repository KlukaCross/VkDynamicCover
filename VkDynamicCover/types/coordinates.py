class Coordinates:
    def __init__(self, x, y):
        self._xy = (x, y)

    @property
    def x(self) -> int:
        return self._xy[0]

    @property
    def y(self) -> int:
        return self._xy[1]
