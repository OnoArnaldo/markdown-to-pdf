from pathlib import Path
from html_to_json import from_file as _from_file, from_string as _from_string

__all__ = ('load', 'loads')


def load(file_file: Path) -> dict:  # pragma: no cover
    return _from_file(file_file)


def loads(text: str) -> dict:  # pragma: no cover
    return _from_string(text)
