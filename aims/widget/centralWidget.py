from PySide6 import QtWidgets

from aims.settings import get_setting
from aims.widget.metaWidget import MetaWidget
from aims.widget.sheetWidget import SheetWidget
from aims.widget.queueWidget import QueueWidget


class CentralWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent=parent)

        # style
        self.setStyleSheet("font-size: 14px; font-weight: 600")

        # layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        #
        self.stackedWidget = QtWidgets.QStackedWidget(parent=self)
        layout.addWidget(self.stackedWidget)

        self.sheetWidget = SheetWidget(parent=self)
        self.stackedWidget.addWidget(self.sheetWidget)

        self.queueWidget = QueueWidget(parent=self)
        self.stackedWidget.addWidget(self.queueWidget)

        #
        self.metaWidget = MetaWidget(
            parent=self,
        )
        layout.addWidget(self.metaWidget)

    # --------        slots        --------
    def _onRefreshTriggered(self):

        # update current widget
        widget = self.queueWidget if get_setting(key='mainWindow/queue-widget') else self.sheetWidget
        widget._onRefreshTriggered()

        # update stacked widget
        self.stackedWidget.setCurrentWidget(widget)

        # update info widget
        self.metaWidget._onRefreshTriggered()
