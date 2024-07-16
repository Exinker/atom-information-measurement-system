from PySide6 import QtWidgets

from aims.core.setting import get_setting
from aims.widget.analisysWidget import AnalysisWidget
from aims.widget.metaWidget import MetaWidget
from aims.widget.probeWidget import ProbeWidget


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

        self.probeWidget = ProbeWidget(parent=self)
        self.stackedWidget.addWidget(self.probeWidget)

        self.analysisWidget = AnalysisWidget(parent=self)
        self.stackedWidget.addWidget(self.analysisWidget)

        #
        self.metaWidget = MetaWidget(
            parent=self,
        )
        layout.addWidget(self.metaWidget)

    # --------        slots        --------
    def _onRefreshTriggered(self):

        # update current widget
        widget = self.analysisWidget if get_setting(key='mainWindow/queue-widget') else self.probeWidget
        widget._onRefreshTriggered()

        # update stacked widget
        self.stackedWidget.setCurrentWidget(widget)

        # update info widget
        self.metaWidget._onRefreshTriggered()
