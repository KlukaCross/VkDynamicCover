class Coordinates:
    def __init__(self, x, y):
        self._xy = (x, y)

    @property
    def x(self) -> int:
        return self._xy[0]

    @property
    def y(self) -> int:
        return self._xy[1]

    def __len__(self):
        return 2

    def __getitem__(self, key):
        return self._xy[key]

    def __add__(self, other):
        return self._xy + other
