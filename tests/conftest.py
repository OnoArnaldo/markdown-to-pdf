import pytest

from pathlib import Path
from reportlab.pdfbase import pdfdoc

ROOT_DIR = Path(__file__).parent.absolute()
FONT_DIR = ROOT_DIR / 'fonts' / 'UbuntuMono'
EXPECTED_PDF_DIR = ROOT_DIR / 'expected_pdf'


class FakePDFDate(pdfdoc.PDFDate):
    def format(self, doc):
        return pdfdoc.format(pdfdoc.PDFString("D:20230728020420-01'00'"), doc)


class FakePDFDocument(pdfdoc.PDFDocument):
    def ID(self):
        self._ID = (b'\n[<165a2d52ed32fb7e44a66e469053d6cc><165a2d52ed32fb7e44a66e469053d6cc>]\n'
                    b'% ReportLab generated PDF document -- digest (http://www.reportlab.com)\n')
        return self._ID


class FakeOutputFile:
    def __init__(self, *args, **kwargs) -> None:
        self.data = b''

    def write(self, data: bytes):
        self.data = data


@pytest.fixture
def output() -> FakeOutputFile:
    orig = pdfdoc.PDFDate
    orig_doc = pdfdoc.PDFDocument

    pdfdoc.PDFDate = FakePDFDate
    pdfdoc.PDFDocument = FakePDFDocument

    yield FakeOutputFile()

    pdfdoc.PDFDate = orig
    pdfdoc.PDFDocument = orig_doc
