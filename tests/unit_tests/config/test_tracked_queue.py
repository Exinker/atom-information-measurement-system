from typing import Any

import pytest

from aims.configs import TrackedQueue


@pytest.fixture(params=[1, 2])
def value(request) -> str:
    return request.param


def test_tracked_queue(
    value: int,
):
    assert TrackedQueue(value) == value


@pytest.mark.parametrize(
    'value', [0, 42, '1'],
)
def test_tracked_queue_invalid(
    value: Any,
):
    with pytest.raises(ValueError):
        assert TrackedQueue(value)
