from datetime import datetime
import pytest
from md2pdf import utils
from md2pdf.utils import ordinal, today_long, append_space


class FakeDateTime:
    def __init__(self, value: datetime) -> None:
        self.value = value

    def utcnow(self) -> datetime:
        return self.value


@pytest.mark.parametrize(
    'value, expected',
    [
        (1, '1st'),
        (2, '2nd'),
        (3, '3rd'),
        (4, '4th'),
        (5, '5th'),
        (11, '11th'),
        (12, '12th'),
        (13, '13th'),
        (14, '14th'),
        (20, '20th'),
        (21, '21st'),
        (22, '22nd'),
        (23, '23rd'),
        (24, '24th'),
    ],
)
def test_ordinal(value, expected):
    assert ordinal(value) == expected


@pytest.mark.parametrize(
    'value, expected',
    [
        (datetime(2023, 7, 10), '10th of July, 2023'),
        (datetime(2023, 8, 1), '1st of August, 2023'),
        (datetime(2025, 9, 23), '23rd of September, 2025'),
    ],
)
def test_today_long(value, expected):
    _datetime = utils.datetime
    utils.datetime = FakeDateTime(value)

    assert today_long() == expected

    utils.datetime = _datetime


@pytest.mark.parametrize(
    'value, expected',
    [
        ('', ''),
        ('abc', 'abc '),
        ('abc ', 'abc '),
    ],
)
def test_append_space(value, expected):
    assert append_space(value) == expected
