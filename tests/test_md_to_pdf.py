from pathlib import Path

import pytest
from reportlab.platypus import Paragraph, ListFlowable, KeepTogether

from md2pdf.config import loads_config, Config
from md2pdf.document import Md2Pdf

ROOT_DIR = Path(__file__).parent
CONFIG_FILE = ROOT_DIR / 'config.toml'

MD = """\
# The title {: #title}

left#center#right
{: .3-columns size=73}

## The subtitle {: .subtitle}

The paragraph:

* item 1
* item 2
* item 3

Formatted: {{ underscore("underscore") }}, {{ italic("italic") }}, 
{{ bold("bold") }},  {{ bold(italic("bold-italic")) }}, {{ italic(bold("italic-bold")) }}

key: value
{: .key-value style="italic,bold,underscore" }

* item1: value1
* item2: value2
* item3: value3
{: .key-value}
"""

MD_WITH_KEEP_TOGETHER = """\
# The title {: #title .keep-together}

## The subtitle {: .subtitle .keep-together}

The paragraph:
{: .keep-together }

* item 1
* item 2
* item 3
"""


class ExpectedParagraph:
    def __init__(self, text, style):
        self.text = text
        self.style = style

    def __eq__(self, other) -> bool:
        if isinstance(other, Paragraph):
            # if not (other.text == self.text and other.style.name == self.style):
            #     print(f'|| {other.text} != {self.text}')
            return other.text == self.text and other.style.name == self.style

        return False


class ExpectedList:
    def __init__(self, values: list[str], bullet_type):
        self.values = values
        self.bullet_type = bullet_type

    def __eq__(self, other) -> bool:
        if isinstance(other, ListFlowable):
            values = [f.text for f in other._flowables]
            return self.values == values and self.bullet_type == other._bulletType

        return False


@pytest.fixture
def config() -> Config:
    return loads_config(CONFIG_FILE.read_text())


def test_generate(config):
    doc = Md2Pdf().setup(config, ROOT_DIR / '..').build_from_md(MD)
    space = '&nbsp;'
    assert doc.elements == [
        ExpectedParagraph('The title', 'Doc1 Title'),
        ExpectedParagraph(f'left{space * 29}center{space * 29}right', 'Doc1 Body'),
        ExpectedParagraph('The subtitle', 'Doc1 subtitle'),
        ExpectedParagraph('The paragraph:', 'Doc1 Body'),
        ExpectedList(['item 1', 'item 2', 'item 3'], 'bullet'),
        ExpectedParagraph('Formatted: <u>underscore</u>, <i>italic</i>, '
                          '<b>bold</b>, <b><i>bold-italic</i></b>, '
                          '<i><b>italic-bold</b></i>', 'Doc1 Body'),
        ExpectedParagraph('<u><b><i>key:</i></b></u> value', 'Doc1 Body'),
        ExpectedList(['<b>item1:</b> value1', '<b>item2:</b> value2', '<b>item3:</b> value3'],
                     'bullet')
    ]


def test_generate_with_keep_together(config):
    doc = Md2Pdf().setup(config, ROOT_DIR / '..').build_from_md(MD_WITH_KEEP_TOGETHER)

    assert len(doc.elements) == 1
    assert isinstance(doc.elements[0], KeepTogether)
    assert doc.elements[0]._content == [
        ExpectedParagraph('The title', 'Doc1 Title'),
        ExpectedParagraph('The subtitle', 'Doc1 Body'),
        ExpectedParagraph('The paragraph:', 'Doc1 Body'),
        ExpectedList(['item 1', 'item 2', 'item 3'], 'bullet'),
    ]
