from typing import get_args

import pytest
from PySide6 import QtGui

import aims.settings
from aims.managers.windows_manager.windows.main_window import MainWindow
from aims.settings import FontSize, get_setting, set_setting
from tests.fakes.settings import fake_settings_factory


def assert_font_size(
    font: QtGui.QFont,
    expected: str,
) -> None:
    assert str(font.pixelSize()) == expected


def assert_font_weight(
    font: QtGui.QFont,
    expected: str,
) -> None:
    assert str(font.pixelSize()) == expected


@pytest.mark.parametrize(
    'expected', get_args(FontSize().value),
)
def test_font_size_valid(
    expected: str,
    main_window: MainWindow,
):
    set_setting(
        key='style/font-size',
        value=expected,
    )

    result = get_setting(key='style/font-size')

    assert result == expected

    main_window.centralWidget().styleSheet()

    assert_font_size(
        font=main_window.centralWidget().sheetQueueWidget.tabWidget.tabBar().font(),
        expected=expected,
    )
    assert_font_size(
        font=main_window.centralWidget().sheetQueueWidget.tabWidget.currentWidget().tableViews[-1].horizontalHeader().font(),
        expected=expected,
    )


@pytest.mark.parametrize(
    ['value', 'expected'],
    [
        (2, FontSize().value),
        (64, FontSize().value),
    ],
)
def test_font_size_invalid(
    value: str,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(aims.settings, 'load_settings', fake_settings_factory(
        fields={'style/font-size': value},
    ))

    result = get_setting(key='style/font-size')

    assert result == expected
