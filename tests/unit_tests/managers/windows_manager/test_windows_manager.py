import pytest
from pytestqt.qtbot import QtBot

from aims.managers.data_manager import DataManager
from aims.managers.windows_manager import WindowsManager


@pytest.fixture
def data_manager():
    return DataManager()


def test_windows_manager_setup(
    data_manager: DataManager,
    qtbot: QtBot,
):
    windows_manager = WindowsManager(
        data_manager=data_manager,
    )

    windows_manager.setup()
