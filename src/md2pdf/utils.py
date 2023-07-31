from datetime import datetime

__all__ = ('SPACE', 'AMPERSAND', 'ordinal', 'today_long', 'append_space')

SPACE = '&nbsp;'
AMPERSAND = '&amp;'


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return f'{n}{suffix}'


def today_long() -> str:
    t = datetime.utcnow()
    day = ordinal(t.day)
    return t.strftime(f'{day} of %B, %Y')


def append_space(value: str) -> str:
    """Append space in the end if needed"""
    if value and not value.endswith(' '):
        return f'{value} '
    return value


def underscore(value: str) -> str:
    return f'&lt;u&gt;{value}&lt;/u&gt;'


def italic(value: str) -> str:
    return f'&lt;i&gt;{value}&lt;/i&gt;'


def bold(value: str) -> str:
    return f'&lt;b&gt;{value}&lt;/b&gt;'
