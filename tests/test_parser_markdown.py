import pytest
from md2pdf.parser import MarkdownParser

NO_HEADERS = ("# THE TITLE {: #the-title }\n"
              "\n"
              "## The Subtitle {: #the-subtitle }\n"
              "\n"
              "* item 1\n"
              "* item 2\n"
              "\n"
              "this is a\n"
              "paragraph\n"
              "{: .the-paragraph }\n")

WITH_HEADERS = (f"name: The Name\n"
                f"organization: The Organization\n"
                f"\n"
                f"{NO_HEADERS}\n")

EXPECTED = ("<h1 id=\"the-title\">THE TITLE</h1>\n"
            "<h2 id=\"the-subtitle\">The Subtitle</h2>\n"
            "<ul>\n"
            "<li>item 1</li>\n"
            "<li>item 2</li>\n"
            "</ul>\n"
            "<p class=\"the-paragraph\">this is a\n"
            "paragraph</p>")


class FakeFile:
    def __init__(self, text) -> None:
        self.text = text

    def read(self) -> str:
        return self.text


@pytest.fixture
def parser() -> MarkdownParser:
    return MarkdownParser()


@pytest.mark.parametrize('text, html, headers', [
    ('', '', {}),
    (NO_HEADERS, EXPECTED, {}),
    (WITH_HEADERS, EXPECTED, {'name': 'The Name', 'organization': 'The Organization'})
])
def test_md_parser(parser, text, html, headers):
    assert parser.from_file(FakeFile(text)) == (html, headers)
    assert parser(text) == (html, headers)
