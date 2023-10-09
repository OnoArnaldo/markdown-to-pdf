# pylint: disable=redefined-outer-name
import pytest
from md2pdf.parser import HtmlParser


@pytest.fixture
def parser() -> HtmlParser:
    return HtmlParser()


@pytest.mark.parametrize(
    'text, headers, expected',
    [
        ('', {}, ''),
        ('no headers {{ value }}', {}, 'no headers '),
        ('with headers {{ value }}', {'value': 'with value'}, 'with headers with value'),
    ],
)
def test_parser(parser, text: str, headers: dict, expected: str):
    assert parser(text, **headers) == expected
