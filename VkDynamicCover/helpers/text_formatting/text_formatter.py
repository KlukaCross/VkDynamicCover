import typing


class FormatterFunction:
    def __init__(self, function: typing.Callable, *args, **kwargs):
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return self._function(*self._args, **self._kwargs)


class TextFormatter:
    def __init__(self, original_text: str, format_dict: typing.Dict[str, FormatterFunction]):
        self._original_text = original_text
        self._format_dict = format_dict

    def get_format_text(self) -> str:
        raise NotImplementedError
