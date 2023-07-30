import pytest

from pathlib import Path
from reportlab.lib.units import mm

from md2pdf.document import PdfGenerator, TA_CENTER, TA_JUSTIFY
from .expected_document import expected_create_element, expected_keep_together

ROOT_DIR = Path(__file__).parent.absolute()
FONT_DIR = ROOT_DIR / 'fonts' / 'UbuntuMono'
EXPECTED_PDF_DIR = ROOT_DIR / 'expected_pdf'


@pytest.fixture
def generator() -> PdfGenerator:
    return PdfGenerator() \
        .add_font_family('UbuntuMono',
                         FONT_DIR / 'UbuntuMono-Regular.ttf',
                         FONT_DIR / 'UbuntuMono-Italic.ttf',
                         FONT_DIR / 'UbuntuMono-Bold.ttf',
                         FONT_DIR / 'UbuntuMono-BoldItalic.ttf',
                         ) \
        .add_style('PDF Title',
                   fontName='UbuntuMono-Bold',
                   fontSize=15,
                   alignment=TA_CENTER) \
        .add_style('PDF Body',
                   fontName='UbuntuMono',
                   fontSize=11,
                   alignment=TA_JUSTIFY)


def test_create_elements(generator, output):
    generator.append_paragraph('The Title', style='PDF Title') \
        .append_spacer(width=10, height=10) \
        .append_bullet_list(['Item1', 'Item2', 'Item3'], style='PDF Body') \
        .append_three_columns_paragraph(['left', 'center', 'right'], size=70, style='PDF Body') \
        .build(output,
               title='The pdf file',
               author='Me Myself',
               subject='PDF test',
               keywords=['pdf', 'test'])

    assert output.data.decode('latin1') == expected_create_element


def test_create_elements_with_keep_together(generator, output):
    generator.append_paragraph('First page', style='PDF Body') \
        .append_spacer(10*mm, 241*mm) \
        .append_paragraph('The Title', style='PDF Title', keep_together=True)\
        .append_paragraph('The paragraph', style='PDF Body') \
        .append_spacer(10 * mm, 235 * mm) \
        .append_paragraph('The Subtitle', style='PDF Title', keep_together=True)\
        .append_paragraph('The detailed paragraph', style='PDF Body', keep_together=True)\
        .append_paragraph('The more detailed paragraph', style='PDF Body')\
        .build(output)

    assert output.data == expected_keep_together


# def test_create_table(generator, output):
#     generator.add_table_style()\
#         .append_table()\
#         .build()
