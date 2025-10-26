import pytest

from aims.configs import TrackedMode


def test_tracked_mode_default():
    assert TrackedMode.default() == TrackedMode.CONVERGENCE_BY_PROBES


@pytest.fixture(params=TrackedMode)
def mode(request) -> TrackedMode:
    return request.param


def test_tracked_mode_from_str(
    mode: TrackedMode,
):
    result = TrackedMode.from_str(mode.value)

    assert result == mode


@pytest.mark.parametrize(
    'mode', [
        'reference-control',
    ],
)
def test_tracked_mode_from_str_invalid(
    mode: str,
):
    with pytest.raises(ValueError):
        TrackedMode.from_str(mode)
