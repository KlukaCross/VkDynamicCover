import typing


class FormatterFunction:
    def __init__(self, function: typing.Callable[[any], typing.Dict[str, any]], *args, **kwargs):
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def __call__(self, *args, **kwargs) -> typing.Dict[str, any]:
        return self._function(*self._args, **self._kwargs)


class TextFormatter:
    def __init__(self, function: FormatterFunction):
        self.function = function

    def get_format_text(self, text) -> str:
        raise NotImplementedError
