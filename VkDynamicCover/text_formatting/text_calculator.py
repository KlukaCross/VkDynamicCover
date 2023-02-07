from .text_formatter import TextFormatter
import numexpr


class TextCalculator(TextFormatter):
    def get_format_text(self, text, *args, **kwargs) -> str:
        text = text.format_map(self.function(*args, **kwargs))
        return self.text_calc(text)

    @staticmethod
    def text_calc(text) -> str:
        return str(numexpr.evaluate(text))
