import os
import sys

import pytest
from pytestqt.qtbot import QtBot

import aims
from aims.managers.data_manager import DataManager
from aims.managers.windows_manager.windows.main_window import MainWindow


@pytest.fixture
def data_manager():
    return DataManager()


@pytest.fixture
def main_window(
    data_manager: DataManager,
    qtbot: QtBot,
) -> MainWindow:
    main_window = MainWindow(
        data_manager=data_manager,
    )
    main_window.show()
    main_window.on_refreshed()

    qtbot.add_widget(main_window)

    return main_window


@pytest.fixture(autouse=True)
def setdefault_environ() -> None:
    os.environ['APPLICATION_NAME'] = 'AIMS'
    os.environ['APPLICATION_VERSION'] = aims.__version__
    os.environ['ORGANIZATION_NAME'] = aims.__organization__

    os.environ['DEPLOY'] = str(hasattr(sys, '_MEIPASS'))
