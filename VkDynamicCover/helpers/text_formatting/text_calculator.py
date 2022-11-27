from text_formatter import TextFormatter
import numexpr


class TextCalculator(TextFormatter):
    def get_format_text(self, text) -> str:
        text = text.format_map(self.function())
        return str(numexpr.evaluate(text))
