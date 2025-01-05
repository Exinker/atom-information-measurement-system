from PySide6 import QtCore

from aims.managers.data_manager import DataManager
from aims.managers.windows_manager.windows.main_window import MainWindow


class WindowsManager:

    def __init__(self, data_manager: DataManager) -> None:

        self.data_manager = data_manager

        self.window = None

    def setup(self) -> None:

        self.window = MainWindow(
            data_manager=self.data_manager,
            flags=QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint,
        )

    def update(self) -> None:

        self.window.on_refreshed()
