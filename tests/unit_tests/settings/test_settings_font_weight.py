from typing import get_args

import pytest

import aims.settings
from aims.settings import FontWeight, get_setting
from tests.fakes._settings import fake_load_settings


@pytest.mark.parametrize(
    'expected', get_args(FontWeight.VALUES),
)
def test_font_weight_valid(
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(aims.settings, 'load_settings', fake_load_settings(
        data={'style/font-weight': expected},
    ))

    result = get_setting(key='style/font-weight')

    assert result == expected


@pytest.mark.parametrize(
    ['value', 'expected'],
    [
        ('300', FontWeight.DEFAULT),
        ('900', FontWeight.DEFAULT),
    ],
)
def test_font_weight_invalid(
    value: str,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(aims.settings, 'load_settings', fake_load_settings(
        data={'style/font-weight': value},
    ))

    result = get_setting(key='style/font-weight')

    assert result == expected
