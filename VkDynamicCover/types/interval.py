class Interval(tuple):
    def __new__(cls, a, b):
        return super(Interval, cls).__new__(cls, (a, b))

    def __init__(self, fr, to):
        self._interval = (fr, to)

    @property
    def fr(self) -> int:
        return self._interval[0]

    @property
    def to(self) -> int:
        return self._interval[1]
