from PySide6 import QtWidgets

from src.core.setting import get_setting
from src.widget.probeWidget import ProbeWidget


def _format_tab_label(label: str) -> str:
    """Format label to represent not empty tab's label."""
    return f'{label:<10}'


class AnalysisWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        n_tabs = get_setting(key='config/tracked_queue')

        # layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.tabWidget = QtWidgets.QTabWidget()
        for _ in range(n_tabs):
            widget = ProbeWidget(
                parent=self,
            )
            self.tabWidget.addTab(widget, '')
        self.tabWidget.setCurrentIndex(0)
        layout.addWidget(self.tabWidget)

    # --------        slots        --------
    def _onRefreshAction(self):
        app = QtWidgets.QApplication.instance()

        #
        for i in range(self.tabWidget.count()):

            # get datum
            try:
                datum = app.data[i]
            except IndexError:
                datum = None

            # update widget
            if datum is None:
                self.tabWidget.setTabEnabled(i, False)
                self.tabWidget.setTabText(i, _format_tab_label(label=''))

            else:
                self.tabWidget.setTabEnabled(i, True)
                self.tabWidget.setTabText(i, _format_tab_label(label=datum.probe_name))

                widget = self.tabWidget.widget(i)
                widget._onRefreshAction(datum=datum)
