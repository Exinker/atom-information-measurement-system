from typing import Any

import pytest

from aims.config import FiltratedSheet


@pytest.fixture(params=['лаборант'])
def value(request) -> str:
    return request.param


def test_filtrated_sheet(
    value: str,
):
    assert FiltratedSheet(value) == value


def test_filtrated_sheet_none():
    assert FiltratedSheet(None) is None


@pytest.mark.parametrize(
    'value', ['', 42],
)
def test_filtrated_sheet_invalid(
    value: Any,
):
    with pytest.raises(ValueError):
        FiltratedSheet(value)
