from typing import Any

import pytest

from aims.config import Separator, DEFAULT_SEP


@pytest.fixture(params=[DEFAULT_SEP])
def value(request) -> str:
    return request.param


def test_separator(
    value: str,
):
    assert Separator(value) == value


def test_separator_none():
    assert Separator(None) is None


@pytest.mark.parametrize(
    'value', ['', 42],
)
def test_separator_invalid(
    value: Any,
):
    with pytest.raises(ValueError):
        Separator(value)
