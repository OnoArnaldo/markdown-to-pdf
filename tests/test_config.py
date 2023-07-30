from pathlib import Path

import pytest

from md2pdf import document
from md2pdf.config import loads_config, load_config, Config

ROOT_DIR = Path(__file__).parent
CONFIG_FILE = ROOT_DIR / 'config.toml'


@pytest.fixture
def config() -> Config:
    with CONFIG_FILE.open() as f:
        return load_config(f)


def test_config_empty():
    config = loads_config('')

    assert config.data == {}


@pytest.mark.parametrize('idx,name,font_name',
                         ([0, 'Doc1Font', 'OpenSans'],
                          [1, 'Doc2Font', 'UbuntuMono']))
def test_config_fonts(config, idx, name, font_name):
    assert len(config.fonts) == 2

    font = config.fonts[idx]
    assert font.name == name
    assert font.regular == f'./tests/fonts/{font_name}/{font_name}-Regular.ttf'
    assert font.bold == f'./tests/fonts/{font_name}/{font_name}-Bold.ttf'
    assert font.italic == f'./tests/fonts/{font_name}/{font_name}-Italic.ttf'
    assert font.bold_italic == f'./tests/fonts/{font_name}/{font_name}-BoldItalic.ttf'


@pytest.mark.parametrize('idx,name,parms',
                         [(0, 'Doc1 Title', [('font_name', 'Doc1Font-Bold'),
                                             ('font_size', 16),
                                             ('space_before', 0),
                                             ('space_after', 20),
                                             ('alignment', document.TA_LEFT)]),
                          (1, 'Doc1 subtitle', [('font_name', 'Doc1Font-Bold'),
                                                ('font_size', 12),
                                                ('space_before', 0),
                                                ('space_after', 10),
                                                ('alignment', document.TA_LEFT)]),
                          (2, 'Doc1 Body', [('font_name', 'Doc1Font')]),
                          (3, 'Doc2 Title', [('font_name', 'Doc2Font-Bold'),
                                             ('font_size', 16),
                                             ('space_before', 0),
                                             ('space_after', 20),
                                             ('alignment', document.TA_LEFT)]),
                          (4, 'Doc2 subtitle', [('font_name', 'Doc2Font-BoldItalic'),
                                                ('font_size', 12),
                                                ('space_before', 0),
                                                ('space_after', 10),
                                                ('alignment', document.TA_LEFT)]),
                          (5, 'Doc2 Body', [('font_name', 'Doc2Font')]),
                          ])
def test_config_styles(config, idx, name, parms):
    assert len(config.styles) == 6

    style = config.styles[idx]
    assert style.name == name

    for key, value in parms:
        assert getattr(style, key) == value
        assert style.strike_width is None


@pytest.mark.parametrize('idx,style,attrs', [
    (0, 'Doc2 Title', [('id', 'title2')]),
    (1, 'Doc2 subtitle', [('id', 'subtitle2')]),
    (2, 'Doc1 Title', [('id', 'title')]),
    (3, 'Doc1 subtitle', [('tag', 'h2'), ('class', 'subtitle')]),
])
def test_config_reports(config, idx, style, attrs):
    assert len(config.reports) == 4

    report = config.reports[idx]
    assert report.style == style

    for attr_idx, (key, value) in enumerate(attrs):
        attr = report.attributes[attr_idx]

        assert attr.name == key
        assert attr.value == value


@pytest.mark.parametrize('key,value', [
    ('font_size', 10),
    ('alignment', 'TA_JUSTIFY'),
    ('allow_widows', 0),
    ('space_before', 10),
    ('space_after', 10),
])
def test_config_defaults_style(config, key, value):
    style = config.defaults.style

    assert getattr(style, key) == (getattr(document, value) if key == 'alignment' else value)
    assert style[key] == value


def test_config_defaults_report(config):
    report = config.defaults.report

    assert report.style == 'Doc1 Body'
    assert report['style'] == 'Doc1 Body'
