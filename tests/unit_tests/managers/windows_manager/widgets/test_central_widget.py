import pytest
from PySide6 import QtWidgets
from pytest import MonkeyPatch
from pytestqt.qtbot import QtBot

from aims.managers.data_manager import DataManager
from aims.managers.windows_manager.widgets.central_widget import CentralWidget
from aims.managers.windows_manager.widgets.sheet_queue_widget import SheetQueueWidget
from aims.managers.windows_manager.widgets.sheet_widget import SheetWidget
from tests.fakes.settings import fake_settings_factory


@pytest.mark.parametrize(
    ['value', 'expected'],
    [
        (True, SheetQueueWidget),
        (False, SheetWidget),
    ],
)
def test_central_widget_refresh(
    data_manager: DataManager,
    value: bool,
    expected: QtWidgets.QWidget,
    monkeypatch: MonkeyPatch,
    qtbot: QtBot,
):
    monkeypatch.setattr('aims.settings.load_settings', fake_settings_factory(
        fields={'mainWindow/queue-widget': value},
    ))
    central_widget = CentralWidget(
        data_manager=data_manager,
        parent=None,
    )

    central_widget.on_refreshed()

    assert isinstance(central_widget.stackedWidget.currentWidget(), expected)
