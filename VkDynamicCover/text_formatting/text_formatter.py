import typing


class FormatterFunction:
    def __init__(self, function: typing.Callable[[any], typing.Dict[str, any]], *args, **kwargs):
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def __call__(self, *args, **kwargs) -> typing.Dict[str, any]:
        args += self._args
        kwargs.update(self._kwargs)
        return self._function(*args, **kwargs)


class TextFormatter:
    def __init__(self, function: FormatterFunction):
        self.function = function

    def get_format_text(self, text, *args, **kwargs) -> str:
        raise NotImplementedError
