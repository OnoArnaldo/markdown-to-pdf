import pytest
from pathlib import Path
from reportlab.platypus import Paragraph, ListFlowable, KeepTogether
from md2pdf.document import Md2Pdf
from md2pdf.config import loads_config, Config

ROOT_DIR = Path(__file__).parent
CONFIG_FILE = ROOT_DIR / 'config.toml'

MD = """\
# The title {: #title}

## The subtitle {: .subtitle}

The paragraph:

* item 1
* item 2
* item 3
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

    assert doc.elements == [
        ExpectedParagraph('The title', 'Doc1 Title'),
        ExpectedParagraph('The subtitle', 'Doc1 subtitle'),
        ExpectedParagraph('The paragraph:', 'Doc1 Body'),
        ExpectedList(['item 1', 'item 2', 'item 3'], 'bullet'),
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