from .text_formatter import TextFormatter
from loguru import logger
import numexpr


class TextCalculator(TextFormatter):
    def get_format_text(self, text, *args, **kwargs) -> str:
        text = text.format_map(self.function(*args, **kwargs))
        return self.text_calc(text)

    @staticmethod
    def text_calc(text) -> str:
        try:
            value = numexpr.evaluate(text)
        except KeyError as e:
            logger.error(e)
            value = 0
        return str(value)
