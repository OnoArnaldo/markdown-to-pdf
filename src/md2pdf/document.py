import typing as _
from pathlib import Path
from hashlib import shake_128
from pickle import dumps as pickle_dumps

from reportlab.lib.units import mm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, StyleSheet1
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable, ListFlowable, KeepTogether
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from .utils import SPACE
from .parser import HtmlParser, MarkdownParser
from .config import camel_case_dict
from . import html_to_dict

if _.TYPE_CHECKING:  # pragma: no cover
    from .config import Config


class Writable(_.Protocol):
    def write(self, data: bytes) -> None:  # pragma: no cover
        ...


class Empty:
    ...


EMPTY = Empty()


class PdfGenerator:
    def __init__(self) -> None:
        self.elements: list[Flowable] = []
        self.styles: StyleSheet1 = getSampleStyleSheet()
        self.keep_together: list[Flowable] = []

    # region BUILDERS
    def build_paragraph(self,
                        text: str = None,
                        style: str = 'Body',
                        bullet_text: str = None,
                        frags: list = None,
                        case_sensitive: int = 1,
                        encoding: str = 'utf8') -> Paragraph:
        return Paragraph(text, self.styles[style], bullet_text, frags, case_sensitive, encoding)

    def build_spacer(self, width: int, height: int, is_glue: bool = False) -> Spacer:
        return Spacer(width, height, is_glue)

    def build_list(self, values: list[str], style: str, bullet_type: str = 'bullet') -> ListFlowable:
        style = self.styles[style]
        return ListFlowable([Paragraph(v, style=style) for v in values], bulletType=bullet_type)

    def build_keep_together(self, flowables: list[Flowable]) -> KeepTogether:
        return KeepTogether(flowables)
    # endregion

    # region ADDERS
    def add_font(self, name: str, ttf_file: Path | str, *, raise_error: bool = True) -> _.Self:
        if isinstance(ttf_file, (Path, str)) and Path(ttf_file).is_file():
            pdfmetrics.registerFont(TTFont(name, ttf_file))

        elif raise_error:
            raise ValueError(f'Font file {ttf_file!s} does not exists.')

        return self

    def add_font_family(self, name: str,
                        regular_path: Path | str,
                        italic_path: Path | str,
                        bold_path: Path | str,
                        bold_italic_path: Path | str) -> _.Self:

        self.add_font(name, regular_path, raise_error=True)
        self.add_font(f'{name}-Italic', italic_path, raise_error=False)
        self.add_font(f'{name}-Bold', bold_path, raise_error=False)
        self.add_font(f'{name}-BoldItalic', bold_italic_path, raise_error=False)

        pdfmetrics.registerFontFamily(name,
                                      normal=name,
                                      bold=f'{name}-Bold',
                                      italic=f'{name}-Italic',
                                      boldItalic=f'{name}-BoldItalic')

        return self

    def add_style(self, name: str, **kwargs) -> _.Self:
        if 'parent' in kwargs:
            kwargs['parent'] = self.styles[kwargs['parent']]

        style = ParagraphStyle(name, **kwargs)
        self.styles.add(style)
        return self

    # endregion

    # region APPENDERS
    def append_element(self, element: Flowable, keep_together: bool = False) -> None:
        if keep_together:
            self.keep_together.append(element)
        elif len(self.keep_together):
            self.keep_together.append(element)
            self.elements.append(
                self.build_keep_together(self.keep_together)
            )

            self.keep_together = []
        else:
            self.elements.append(element)

    def append_paragraph(self,
                         text: str = None,
                         style: str = 'Body',
                         bullet_text: str = None,
                         frags: list = None,
                         case_sensitive: int = 1,
                         encoding: str = 'utf8',
                         keep_together: bool = False) -> _.Self:
        paragraph = self.build_paragraph(text, style, bullet_text, frags, case_sensitive, encoding)

        self.append_element(paragraph, keep_together)

        return self

    def append_spacer(self, width: int, height: int, is_glue: bool = False, keep_together: bool = False) -> _.Self:
        spacer = self.build_spacer(width, height, is_glue)
        self.append_element(spacer, keep_together)
        return self

    def append_three_columns_paragraph(self,
                                       texts: _.Iterable[str],
                                       size: int,
                                       style: str,
                                       bullet_text: bool = None,
                                       frags: list = None,
                                       case_sensitive: int = 1,
                                       encoding: str = 'utf8',
                                       keep_together: bool = False
                                       ) -> _.Self:
        left, center, right = texts
        center_size = len(center)
        left_size, remainder = divmod(size - center_size, 2)

        text = f'{left:<{left_size}}{center}{right:>{left_size + remainder}}'.replace(' ', SPACE)

        return self.append_paragraph(text, style, bullet_text, frags, case_sensitive, encoding, keep_together)

    def append_bullet_list(self,
                           values: list[str],
                           style: str,
                           bullet_type: str = 'bullet',
                           keep_together: bool = False) -> _.Self:
        bullet_list = self.build_list(values, style, bullet_type)

        self.append_element(bullet_list, keep_together)

        return self
    # endregion

    def build(self, file_name: str | Path | Writable, *,
              title: str = '',
              author: str = '',
              subject: str = '',
              keywords: _.Iterable[str] = None,
              creator: str = '',
              **kwargs) -> None:
        doc = SimpleDocTemplate(file_name,
                                pagesize=A4,
                                rightMargin=20 * mm,
                                leftMargin=20 * mm,
                                topMargin=20 * mm,
                                bottomMargin=20 * mm,
                                **kwargs)

        doc.title = title
        doc.author = author
        doc.subject = subject
        doc.keywords = keywords
        doc.creator = creator

        doc.build(self.elements)

    @classmethod
    def version(cls, data: _.Any) -> str:
        return shake_128(pickle_dumps(data)).hexdigest(4)

    def save(self, file_name: Path | Writable, **meta) -> None:
        name = meta.get('name', '')
        version = meta.get('version', '')

        if isinstance(file_name, Path):
            file_name = str(file_name)

        self.build(file_name,
                   title=meta.get('title', ''),
                   author=name,
                   creator=name,
                   subject=f'version="{version}"',
                   keywords=meta.get('keywords', []),
                   )


class Md2Pdf(PdfGenerator):
    def __init__(self) -> None:
        super().__init__()

        self.config: 'Config | None' = None
        self.root_dir: Path | str | None = None
        self.html_parser = HtmlParser()
        self.md_parser = MarkdownParser()

    def setup(self, config: 'Config', root_dir: Path | str = None) -> _.Self:
        self.config = config
        self.root_dir = Path(root_dir or '.')

        for font in self.config.fonts:
            self.add_font_family(font.name,
                                 self.root_dir / font.regular,
                                 self.root_dir / font.italic,
                                 self.root_dir / font.bold,
                                 self.root_dir / font.bold_italic)

        default = self.config.defaults.style
        for style in self.config.styles:
            style = style.__class__({**default, **style})
            self.add_style(**camel_case_dict(style))

        return self

    def _get_elem_attr(self, element: dict, name: str) -> str:
        if name == 'tag':
            return element[name]
        return element['attributes'].get(name, EMPTY)

    def _find_report_config(self, element: dict) -> dict:
        for report in self.config.reports:
            if all(self._get_elem_attr(element, a['name']) == a['value'] for a in report.attributes):
                return report

    def build_from_data(self, data: dict) -> _.Self:
        for child in data.get('children', []):
            config = self._find_report_config(child)

            if config is None:
                config = self.config.defaults.report

            config = {} if config is None else dict(config)
            if 'attributes' in config:
                del config['attributes']

            classes = child.get('attributes', {}).get('class', '').split(' ')
            if child.get('tag') in {f'h{i}' for i in range(1, 7)} | {'p'}:
                self.append_paragraph(child.get('value', ''),
                                      style=config.get('style'),
                                      keep_together='keep-together' in classes)

            elif child.get('tag') in {'ul'}:
                self.append_bullet_list(
                    [c.get('value', '') for c in child.get('children', [])],
                    style=config.get('style'),
                    keep_together='keep-together' in classes
                )

        return self

    def build_from_html(self, text: str, **kwargs) -> _.Self:
        text = self.html_parser(text, **kwargs)
        data = html_to_dict.loads(f'<data>{text}</data>')

        return self.build_from_data(data)

    def build_from_md(self, text: str) -> _.Self:
        text, kwargs = self.md_parser(text)

        return self.build_from_html(text, **kwargs)

    def build_from_file(self, md_file: str | Path) -> _.Self:
        with Path(md_file).open() as f:
            text, kwargs = self.md_parser.from_file(f)

        return self.build_from_html(text, **kwargs)
