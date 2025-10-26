import pytest

from aims.configs import TrackedPediod


def test_tracked_pediod_default():

    assert TrackedPediod.default() == TrackedPediod.ALL


@pytest.fixture(params=TrackedPediod)
def pediod(request) -> TrackedPediod:
    return request.param


def test_tracked_pediod_from_str(
    pediod: TrackedPediod,
):

    result = TrackedPediod.from_str(pediod.value)

    assert result == pediod


@pytest.mark.parametrize(
    'pediod', [
        'night',
    ],
)
def test_tracked_pediod_from_str_invalid(
    pediod: str,
):

    with pytest.raises(ValueError):
        TrackedPediod.from_str(pediod)
