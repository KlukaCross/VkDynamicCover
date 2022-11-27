from text_formatter import TextFormatter
from loguru import logger
import re


class TextInserter(TextFormatter):
    def get_format_text(self, text: str, *args, **kwargs) -> str:
        return text.format_map(self.function(*args, **kwargs))
