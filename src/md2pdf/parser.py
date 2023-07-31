import typing as _
import markdown
from jinja2 import Environment, BaseLoader, select_autoescape

from .utils import AMPERSAND, today_long, append_space, underscore, italic, bold

__all__ = ('HtmlParser', 'MarkdownParser')

SourceType = tuple[str, _.Optional[str], _.Optional[_.Callable[[], bool]]]


class Readable(_.Protocol):
    def read(self) -> str:  # pragma: no cover
        ...


def build_env(loader: BaseLoader) -> Environment:
    env = Environment(loader=loader,
                      autoescape=select_autoescape(('html', 'xml')),
                      trim_blocks=True,
                      lstrip_blocks=True)
    env.globals['today'] = today_long
    env.globals['space'] = append_space
    env.globals['underscore'] = underscore
    env.globals['italic'] = italic
    env.globals['bold'] = bold

    return env


class ParserLoader(BaseLoader):
    def __init__(self) -> None:
        self.template: str = ''
        self.source: str = ''

    def load_source(self, template: str, source: str) -> None:
        self.template = template
        self.source = source

    def get_source(self, environment: 'Environment', template: str) -> SourceType:
        source = self.source if template == self.template else ''
        return source.replace('&', AMPERSAND), f'{template}.md', lambda: True


class HtmlParser:
    def __init__(self):
        self.loader = ParserLoader()
        self.env = build_env(loader=self.loader)

    def __call__(self, text: str, *args, **kwargs) -> str:
        return self.parse(text, *args, **kwargs)

    def parse(self, text: str, *args, **kwargs) -> str:
        self.loader.load_source('html-parser', text)

        template = self.env.get_template('html-parser')
        return template.render(*args, **kwargs)


class MarkdownParser:
    def __init__(self):
        self.extensions = ('meta', 'attr_list', 'tables')

    def __call__(self, text: str) -> tuple[str, dict]:
        return self._parse(text)

    def _parse_value(self, value: list) -> _.Any:
        return value[0] if len(value) == 1 else value

    def _parse(self, text: str) -> tuple[str, dict]:
        mk = markdown.Markdown(extensions=self.extensions)
        content = mk.convert(text)
        headers = {k: self._parse_value(v) for k, v in mk.Meta.items()}

        return content, headers

    def from_file(self, f: Readable) -> tuple[str, dict]:
        return self._parse(f.read())
