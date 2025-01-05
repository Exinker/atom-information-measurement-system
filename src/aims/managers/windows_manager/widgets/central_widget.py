from PySide6 import QtWidgets

from aims.managers.data_manager import DataManager
from aims.managers.windows_manager.widgets.sheet_queue_widget import SheetQueueWidget
from aims.managers.windows_manager.widgets.sheet_widget import SheetWidget
from aims.settings import get_setting


class CentralWidget(QtWidgets.QWidget):

    def __init__(self, data_manager: DataManager, parent: QtWidgets.QWidget | None):
        super().__init__(parent=parent)

        self.data_manager = data_manager

        # style
        self.setStyleSheet("font-size: 14px; font-weight: 600")

        # layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # stacked widget
        self.stackedWidget = QtWidgets.QStackedWidget(parent=self)
        layout.addWidget(self.stackedWidget)

        self.sheetWidget = SheetWidget(
            data_manager=self.data_manager,
            parent=self,
        )
        self.stackedWidget.addWidget(self.sheetWidget)

        self.sheetQueueWidget = SheetQueueWidget(
            data_manager=self.data_manager,
            parent=self,
        )
        self.stackedWidget.addWidget(self.sheetQueueWidget)

    def _on_refresh_triggered(self):

        # update stacked widget
        widget = self.sheetQueueWidget if get_setting(key='mainWindow/queue-widget') else self.sheetWidget
        widget._on_refresh_triggered()

        self.stackedWidget.setCurrentWidget(widget)
