import typing as _
import re
import tomllib
from collections import UserDict
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT

__all__ = ('load_config', 'loads_config', 'camel_case_dict',
           'Style', 'Font', 'ReportAttribute',
           'Report', 'Config')


RE_CAMEL_CASE = re.compile(r'_[a-z]')


def camel_case_key(key: str) -> str:
    for val in set(RE_CAMEL_CASE.findall(key)):
        key = key.replace(val, val[-1].upper())
    return key


def camel_case_dict(data: UserDict) -> dict:
    return {camel_case_key(k): getattr(data, k)
            for k, v in vars(data.__class__).items()
            if isinstance(v, property) and getattr(data, k) is not None}


class Style(UserDict):
    @property
    def name(self):
        return self.get('name')

    @property
    def font_name(self) -> str:
        return self.get('font_name')

    @property
    def font_size(self) -> str:
        return self.get('font_size')

    @property
    def leading(self) -> str:
        return self.get('leading')

    @property
    def left_indent(self) -> str:
        return self.get('left_indent')

    @property
    def right_indent(self) -> str:
        return self.get('right_indent')

    @property
    def first_line_indent(self) -> str:
        return self.get('first_line_indent')

    @property
    def alignment(self) -> str:
        match self.get('alignment'):
            case 'TA_LEFT':
                return TA_LEFT
            case 'TA_CENTER':
                return TA_CENTER
            case 'TA_RIGHT':
                return TA_RIGHT
            case 'TA_JUSTIFY':
                return TA_JUSTIFY

    @property
    def space_before(self) -> str:
        return self.get('space_before')

    @property
    def space_after(self) -> str:
        return self.get('space_after')

    @property
    def bullet_font_name(self) -> str:
        return self.get('bullet_font_name')

    @property
    def bullet_font_size(self) -> str:
        return self.get('bullet_font_size')

    @property
    def bullet_indent(self) -> str:
        return self.get('bullet_indent')

    @property
    def text_color(self) -> str:
        return self.get('text_color')

    @property
    def back_color(self) -> str:
        return self.get('back_color')

    @property
    def word_wrap(self) -> str:
        return self.get('word_wrap')

    @property
    def border_width(self) -> str:
        return self.get('border_width')

    @property
    def border_padding(self) -> str:
        return self.get('border_padding')

    @property
    def border_color(self) -> str:
        return self.get('border_color')

    @property
    def border_radius(self) -> str:
        return self.get('border_radius')

    @property
    def allow_widows(self) -> str:
        return self.get('allow_widows')

    @property
    def allow_orphans(self) -> str:
        return self.get('allow_orphans')

    @property
    def text_transform(self) -> str:
        return self.get('text_transform')

    @property
    def end_dots(self) -> str:
        return self.get('end_dots')

    @property
    def split_long_words(self) -> str:
        return self.get('split_long_words')

    @property
    def underline_width(self) -> str:
        return self.get('underline_width')

    @property
    def bullet_anchor(self) -> str:
        return self.get('bullet_anchor')

    @property
    def justify_last_line(self) -> str:
        return self.get('justify_last_line')

    @property
    def justify_breaks(self) -> str:
        return self.get('justify_breaks')

    @property
    def space_shrinkage(self) -> str:
        return self.get('space_shrinkage')

    @property
    def strike_width(self) -> int:
        return self.get('strike_width')

    @property
    def underline_offset(self) -> str:
        return self.get('underline_offset')

    @property
    def underline_gap(self) -> str:
        return self.get('underline_gap')

    @property
    def strike_offset(self) -> str:
        return self.get('strike_offset')

    @property
    def strike_gap(self) -> str:
        return self.get('strike_gap')

    @property
    def link_underline(self) -> str:
        return self.get('link_underline')

    @property
    def hyphenation_lang(self) -> str:
        return self.get('hyphenation_lang')

    @property
    def uri_waste_reduce(self) -> int:
        return self.get('uri_waste_reduce')

    @property
    def embedded_hyphenation(self) -> str:
        return self.get('embedded_hyphenation')


class Font(UserDict):
    @property
    def name(self) -> str:
        return self.get('name')

    @property
    def regular(self) -> str:
        return self.get('regular')

    @property
    def bold(self):
        return self.get('bold')

    @property
    def italic(self):
        return self.get('italic')

    @property
    def bold_italic(self):
        return self.get('bold_italic')


class ReportAttribute(UserDict):
    @property
    def name(self):
        return self.get('name')

    @property
    def value(self):
        return self.get('value')


class Report(UserDict):
    @property
    def style(self):
        return self.get('style')

    @property
    def attributes(self):
        return [ReportAttribute(**kw) for kw in self.get('attributes', [])]


class Defaults(UserDict):
    @property
    def style(self) -> Style:
        return Style(**self.get('style', {}))

    @property
    def report(self) -> Report:
        return Report(**self.get('report', {}))


class Config(UserDict):
    @property
    def fonts(self) -> list[Font]:
        return [Font(**kw) for kw in self.get('fonts', [])]

    @property
    def styles(self) -> list[Style]:
        return [Style(**kw) for kw in self.get('styles', [])]

    @property
    def reports(self) -> list[Report]:
        return [Report(**kw) for kw in self.get('reports', [])]

    @property
    def defaults(self) -> Defaults:
        return Defaults(self.get('defaults', {}))


class FileLike(_.Protocol):
    def read(self) -> str | bytes:  # pragma: no cover
        ...


def load_config(file: FileLike) -> Config:
    return loads_config(file.read())


def loads_config(config: str | bytes) -> Config:
    return Config(tomllib.loads(config))
