class Coordinates:
    def __init__(self, *args):
        if len(args) == 1:
            self._xy = tuple(args[0])
        elif len(args) == 2:
            self._xy = (args[0], args[1])
        else:
            raise ValueError("args len must be 1 or 2")

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
