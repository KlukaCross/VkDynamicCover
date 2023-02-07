import typing
import re

from VkDynamicCover.builders.widget_builder import WidgetBuilder
from VkDynamicCover.widgets.text import TextControl, TextDrawer, TextDesigner, TextInfo, \
    LimitedTextDesigner, LimitedTextInfo, SpacedTextDesigner, SpacedTextInfo, \
    FormattingTextInfo, FormattingTextDesigner, MultipleTextDesigner, MultipleTextInfo, CalcTextDesigner, CalcTextInfo
from loguru import logger


class TextBuilder(WidgetBuilder):
    def create(self, **kwargs) -> TextControl:
        drawer = TextDrawer()
        if not self._is_formatting_text(**kwargs) and not self._is_spaced_text(**kwargs) \
                and not self._is_limited_text(**kwargs) and not self._is_calc_text(**kwargs):
            designer = TextDesigner()
            info = TextInfo(**kwargs)
            return TextControl(drawer=drawer, designer=designer, info=info)
        designers = []
        infos = []
        if self._is_formatting_text(**kwargs):
            designers.append(FormattingTextDesigner())
            infos.append(FormattingTextInfo(**kwargs))
        if self._is_limited_text(**kwargs):
            designers.append(LimitedTextDesigner())
            infos.append(LimitedTextInfo(**kwargs))
        if self._is_calc_text(**kwargs):
            designers.append(CalcTextDesigner())
            infos.append(CalcTextInfo(**kwargs))
        if self._is_spaced_text(**kwargs):
            designers.append(SpacedTextDesigner())
            infos.append(SpacedTextInfo(**kwargs))
        return TextControl(drawer=drawer, designer=MultipleTextDesigner(designers), info=MultipleTextInfo(infos, **kwargs))

    def _is_formatting_text(self, **kwargs) -> bool:
        return re.search(r'\{.*}', kwargs.get("text", "")) is not None

    def _is_spaced_text(self, **kwargs) -> bool:
        return kwargs.get("space_type") is not None

    def _is_limited_text(self, **kwargs) -> bool:
        return re.search(r'\[.*]\[\d+]', kwargs.get("text", "")) is not None

    def _is_calc_text(self, **kwargs) -> bool:
        return re.search(r'<[^<>]*>', kwargs.get("text", "")) is not None

