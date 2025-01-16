from datetime import datetime

import pandas as pd
import pytest

from aims.config import TrackedPediod


@pytest.fixture(params=TrackedPediod)
def tracked_pediod(request) -> TrackedPediod:
    return request.param


def test_tracked_pediod_default():
    assert TrackedPediod.default() == TrackedPediod.ALL


def test_tracked_pediod_from_str(
    tracked_pediod: TrackedPediod,
):
    result = TrackedPediod.from_str(tracked_pediod.value)

    assert result == tracked_pediod


@pytest.mark.parametrize(
    'value', ['evening', 'night', 'morning'],
)
def test_tracked_pediod_from_str_invalid(
    value: str,
):
    with pytest.raises(ValueError):
        TrackedPediod.from_str(value)


def test_tracked_pediod_check_created_at_now(
    tracked_pediod: TrackedPediod,
):
    status = tracked_pediod.check(
        created_at=datetime.now(),
    )

    assert status is True


@pytest.mark.parametrize(
    ['tracked_pediod', 'offset'], [
        (TrackedPediod.YEAR, pd.offsets.DateOffset(years=1)),
        (TrackedPediod.MONTH, pd.offsets.DateOffset(months=1)),
        (TrackedPediod.WEEK, pd.offsets.DateOffset(weeks=1)),
        (TrackedPediod.DAY, pd.offsets.DateOffset(days=1)),
    ],
)
def test_tracked_pediod_check_negative(
    tracked_pediod: TrackedPediod,
    offset: datetime,
):

    status = tracked_pediod.check(
        created_at=datetime.now() - offset,
    )

    assert status is False
