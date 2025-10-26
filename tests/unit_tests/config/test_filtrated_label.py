import pytest

from aims.configs import FiltratedLabel


def test_filtrated_label_default():
    assert FiltratedLabel.default() == FiltratedLabel.NONE


@pytest.fixture(params=FiltratedLabel)
def pediod(request) -> FiltratedLabel:
    return request.param


def test_filtrated_label_from_str(
    pediod: FiltratedLabel,
):
    result = FiltratedLabel.from_str(pediod.value)

    assert result == pediod


@pytest.mark.parametrize(
    'pediod', [
        'superman',
    ],
)
def test_filtrated_label_from_str_invalid(
    pediod: str,
):
    with pytest.raises(ValueError):
        FiltratedLabel.from_str(pediod)
