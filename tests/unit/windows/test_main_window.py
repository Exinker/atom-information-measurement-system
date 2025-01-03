import pytest
import pytestqt

import aims
from aims.managers.data_manager import DataManager
from aims.managers.data_manager.data import (
    ConvergenceByParallelsData,
    ConvergenceByProbesData,
    DataABC,
)
from aims.managers.windows_manager.windows.mainWindow import MainWindow


@pytest.mark.parametrize(
    'data', [
        ConvergenceByParallelsData([]),
        ConvergenceByProbesData([]),
    ],
)
def test_title_default(
    data: DataABC,
    qtbot: pytestqt.qtbot.QtBot,
):
    window = MainWindow(
        data_manager=DataManager(),
    )
    window._update_title()

    assert window.windowTitle() == '{name} {version}'.format(
        name=aims.__name__,
        version=aims.__version__,
    )
