from typing import get_args

import pytest

import aims.settings
from aims.settings import FontSize, get_setting
from tests.fakes.settings import fake_load_settings


@pytest.mark.parametrize(
    'expected', get_args(FontSize.VALUES),
)
def test_font_size_valid(
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(aims.settings, 'load_settings', fake_load_settings(
        data={'style/font-size': expected},
    ))

    result = get_setting(key='style/font-size')

    assert result == expected


@pytest.mark.parametrize(
    ['value', 'expected'],
    [
        ('10', FontSize.DEFAULT),
        ('20', FontSize.DEFAULT),
    ],
)
def test_font_size_invalid(
    value: str,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(aims.settings, 'load_settings', fake_load_settings(
        data={'style/font-size': value},
    ))

    result = get_setting(key='style/font-size')

    assert result == expected
