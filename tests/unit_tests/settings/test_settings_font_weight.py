import pytest

import aims.settings
from aims.settings import FontWeight, get_setting
from tests.fakes.settings import fake_settings_factory


@pytest.mark.parametrize(
    'expected', [200, 400, 600],
)
def test_font_weight_valid(
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(aims.settings, 'load_settings', fake_settings_factory(
        fields={'style/font-weight': expected},
    ))

    result = get_setting(key='style/font-weight')

    assert result == expected


@pytest.mark.parametrize(
    ['value', 'expected'],
    [
        (300, FontWeight().value),
        (900, FontWeight().value),
    ],
)
def test_font_weight_invalid(
    value: str,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(aims.settings, 'load_settings', fake_settings_factory(
        fields={'style/font-weight': value},
    ))

    result = get_setting(key='style/font-weight')

    assert result == expected
